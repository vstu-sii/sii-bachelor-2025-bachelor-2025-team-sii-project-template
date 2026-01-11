"""
A/B тестирование различных промптов для оценки чистоты квартир
"""
import asyncio
import json
import random
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ml.service.model_service import LLMAsyncService
from ml.tracing.langfuse_config import tracer

class ABTestExperiment:
    """Класс для проведения A/B тестирования промптов"""
    
    def __init__(self, service: LLMAsyncService):
        self.service = service
        self.results = []
        self.experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Определяем метрики для оценки
        self.metrics = [
            "response_time",
            "token_count", 
            "score_consistency",
            "defects_count",
            "response_quality"
        ]
    
    async def run_experiment(
        self,
        image_pairs: List[Tuple[str, str]],
        variants: List[str] = None,
        iterations: int = 3,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Запуск A/B тестирования
        
        Args:
            image_pairs: Список пар изображений (чистое, грязное)
            variants: Варианты промптов для тестирования
            iterations: Количество итераций для каждого варианта
            user_id: ID пользователя для трассировки
            
        Returns:
            Результаты эксперимента
        """
        if not variants:
            variants = list(self.service.prompt_variants.keys())
        
        print(f"Starting A/B test: {self.experiment_id}")
        print(f"Variants: {variants}")
        print(f"Image pairs: {len(image_pairs)}")
        print(f"Iterations: {iterations}")
        
        experiment_results = {
            "experiment_id": self.experiment_id,
            "start_time": datetime.now().isoformat(),
            "variants": variants,
            "total_tests": len(image_pairs) * len(variants) * iterations,
            "results": []
        }
        
        # Запускаем тесты для каждой пары изображений
        for pair_idx, (clean_path, dirty_path) in enumerate(image_pairs):
            print(f"\nProcessing image pair {pair_idx + 1}/{len(image_pairs)}")
            
            for variant in variants:
                print(f"  Testing variant: {variant}")
                
                variant_results = []
                
                for iteration in range(iterations):
                    trace_id = f"{self.experiment_id}_{pair_idx}_{variant}_{iteration}"
                    
                    try:
                        start_time = datetime.now()
                        
                        # Выполняем анализ
                        response, metrics = await self.service.analyze_cleanliness(
                            clean_image_path=clean_path,
                            dirty_image_path=dirty_path,
                            prompt_variant=variant,
                            use_cache=False,  # Отключаем кэш для чистоты эксперимента
                            user_id=user_id,
                            trace_id=trace_id
                        )
                        
                        elapsed = (datetime.now() - start_time).total_seconds()
                        
                        # Оцениваем качество ответа
                        quality_score = self._evaluate_response_quality(response)
                        
                        # Сохраняем результат
                        result = {
                            "pair_id": pair_idx,
                            "variant": variant,
                            "iteration": iteration,
                            "trace_id": trace_id,
                            "response_time": elapsed,
                            "metrics": {
                                "inference_time": metrics.inference_time,
                                "token_count": metrics.token_count,
                                "cache_hit": metrics.cache_hit
                            },
                            "response": {
                                "score": response.score,
                                "defects_count": len(response.defects),
                                "defects": response.defects[:3],  # Первые 3 недостатка
                                "quality_score": quality_score
                            },
                            "success": response.success
                        }
                        
                        variant_results.append(result)
                        self.results.append(result)
                        
                        print(f"    Iteration {iteration + 1}: "
                              f"score={response.score}, "
                              f"time={elapsed:.2f}s, "
                              f"tokens={metrics.token_count}, "
                              f"quality={quality_score:.2f}")
                        
                    except Exception as e:
                        print(f"    Iteration {iteration + 1}: ❌ Error: {e}")
                        
                        error_result = {
                            "pair_id": pair_idx,
                            "variant": variant,
                            "iteration": iteration,
                            "error": str(e),
                            "success": False
                        }
                        
                        variant_results.append(error_result)
                        self.results.append(error_result)
                
                # Статистика по варианту для этой пары изображений
                if variant_results:
                    self._calculate_variant_stats(variant, variant_results)
        
        experiment_results["end_time"] = datetime.now().isoformat()
        experiment_results["results"] = self.results
        
        # Анализ результатов
        analysis = self.analyze_results()
        experiment_results["analysis"] = analysis
        
        # Сохранение результатов
        self.save_results(experiment_results)
        
        return experiment_results
    
    def _evaluate_response_quality(self, response) -> float:
        """
        Оценка качества ответа модели (0-1)
        
        Метрики:
        - Корректность формата
        - Содержательность недостатков
        - Уместность рекомендаций
        - Консистентность оценки
        """
        quality_score = 0.0
        
        # 1. Проверка формата (0.3 балла)
        if response.raw_response:
            has_defects = "Недостатки:" in response.raw_response
            has_score = "Оценка:" in response.raw_response
            has_recommendations = "Рекомендации:" in response.raw_response
            
            if has_defects and has_score and has_recommendations:
                quality_score += 0.3
        
        # 2. Содержательность недостатков (0.3 балла)
        if response.defects:
            # Проверяем, что недостатки не общие
            generic_phrases = ["недостатки не обнаружены", "все чисто", "идеально"]
            specific_defects = [
                d for d in response.defects 
                if not any(phrase in d.lower() for phrase in generic_phrases)
            ]
            
            if specific_defects:
                quality_score += 0.3
        
        # 3. Консистентность оценки (0.2 балла)
        if 0 <= response.score <= 10:
            # Оценка должна соответствовать количеству недостатков
            expected_score = max(0, 10 - len(response.defects) * 2)
            score_diff = abs(response.score - expected_score)
            
            if score_diff <= 2:
                quality_score += 0.2
        
        # 4. Качество рекомендаций (0.2 балла)
        if response.recommendations and len(response.recommendations) > 20:
            # Проверяем, что рекомендации конкретные
            specific_keywords = ["протереть", "помыть", "убрать", "почистить", "вынести"]
            if any(keyword in response.recommendations.lower() for keyword in specific_keywords):
                quality_score += 0.2
        
        return min(1.0, quality_score)
    
    def _calculate_variant_stats(self, variant: str, results: List[Dict]):
        """Рассчитывает статистику по варианту промпта"""
        successful = [r for r in results if r.get("success", False)]
        
        if not successful:
            return
        
        stats = {
            "variant": variant,
            "total_tests": len(results),
            "success_rate": len(successful) / len(results),
            "avg_response_time": statistics.mean([r.get("response_time", 0) for r in successful]),
            "avg_token_count": statistics.mean([r.get("metrics", {}).get("token_count", 0) for r in successful]),
            "avg_score": statistics.mean([r.get("response", {}).get("score", 0) for r in successful]),
            "avg_quality": statistics.mean([r.get("response", {}).get("quality_score", 0) for r in successful])
        }
        
        print(f"  📊 {variant} stats: "
              f"success={stats['success_rate']:.1%}, "
              f"time={stats['avg_response_time']:.2f}s, "
              f"tokens={stats['avg_token_count']:.0f}, "
              f"quality={stats['avg_quality']:.2f}")
    
    def analyze_results(self) -> Dict:
        """Анализ результатов A/B тестирования"""
        
        if not self.results:
            return {}
        
        # Фильтруем успешные тесты
        successful = [r for r in self.results if r.get("success", False)]
        
        if not successful:
            return {"error": "No successful tests"}
        
        df = pd.DataFrame(successful)
        
        # Группировка по вариантам
        grouped = df.groupby("variant")
        
        analysis = {
            "overall": {
                "total_tests": len(self.results),
                "successful_tests": len(successful),
                "success_rate": len(successful) / len(self.results),
                "avg_response_time": df["response_time"].mean(),
                "avg_quality_score": df["response"].apply(lambda x: x.get("quality_score", 0)).mean()
            },
            "variants": {},
            "recommendations": []
        }
        
        # Анализ по вариантам
        for variant, group in grouped:
            variant_data = {
                "test_count": len(group),
                "success_rate": len(group) / len(group),  # Все успешные
                "response_time": {
                    "mean": group["response_time"].mean(),
                    "std": group["response_time"].std(),
                    "min": group["response_time"].min(),
                    "max": group["response_time"].max()
                },
                "quality": {
                    "mean": group["response"].apply(lambda x: x.get("quality_score", 0)).mean(),
                    "std": group["response"].apply(lambda x: x.get("quality_score", 0)).std()
                },
                "scores": {
                    "mean": group["response"].apply(lambda x: x.get("score", 0)).mean(),
                    "distribution": group["response"].apply(lambda x: x.get("score", 0)).value_counts().to_dict()
                },
                "tokens": {
                    "mean": group["metrics"].apply(lambda x: x.get("token_count", 0)).mean(),
                    "total": group["metrics"].apply(lambda x: x.get("token_count", 0)).sum()
                }
            }
            
            analysis["variants"][variant] = variant_data
        
        # Определение победителя
        winner = self._determine_winner(analysis)
        analysis["winner"] = winner
        
        # Рекомендации
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _determine_winner(self, analysis: Dict) -> Dict:
        """Определение лучшего варианта промпта"""
        
        variants = analysis.get("variants", {})
        if not variants:
            return {}
        
        # Веса метрик
        weights = {
            "response_time": 0.25,      # Быстрее - лучше
            "quality": 0.35,            # Качество ответа
            "tokens": 0.20,             # Эффективность
            "success_rate": 0.20        # Надежность
        }
        
        scores = {}
        
        for variant, data in variants.items():
            score = 0
            
            # Response time score (обратная зависимость)
            if data["response_time"]["mean"] > 0:
                time_score = 1 / data["response_time"]["mean"]
                score += time_score * weights["response_time"]
            
            # Quality score
            quality = data["quality"]["mean"]
            score += quality * weights["quality"]
            
            # Token efficiency (обратная зависимость)
            if data["tokens"]["mean"] > 0:
                token_score = 1000 / data["tokens"]["mean"]  # Нормализация
                score += min(token_score, 1) * weights["tokens"]
            
            # Success rate
            success = data["success_rate"]
            score += success * weights["success_rate"]
            
            scores[variant] = score
        
        # Находим победителя
        winner_variant = max(scores.items(), key=lambda x: x[1])
        
        return {
            "variant": winner_variant[0],
            "score": winner_variant[1],
            "all_scores": scores
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Генерация рекомендаций на основе результатов"""
        
        recommendations = []
        variants = analysis.get("variants", {})
        
        if not variants:
            return ["Недостаточно данных для рекомендаций"]
        
        # Анализ response time
        times = {v: data["response_time"]["mean"] for v, data in variants.items()}
        fastest = min(times.items(), key=lambda x: x[1])
        slowest = max(times.items(), key=lambda x: x[1])
        
        if fastest[1] < slowest[1] * 0.7:  # На 30% быстрее
            recommendations.append(
                f"Вариант {fastest[0]} значительно быстрее ({fastest[1]:.2f}с vs {slowest[1]:.2f}с)"
            )
        
        # Анализ качества
        qualities = {v: data["quality"]["mean"] for v, data in variants.items()}
        best_quality = max(qualities.items(), key=lambda x: x[1])
        
        if best_quality[1] > 0.7:
            recommendations.append(
                f"Вариант {best_quality[0]} показывает высокое качество ответов ({best_quality[1]:.2f})"
            )
        
        # Анализ эффективности токенов
        tokens = {v: data["tokens"]["mean"] for v, data in variants.items()}
        most_efficient = min(tokens.items(), key=lambda x: x[1])
        
        if most_efficient[1] < 500:  # Менее 500 токенов
            recommendations.append(
                f"Вариант {most_efficient[0]} наиболее эффективен по токенам ({most_efficient[1]:.0f} токенов)"
            )
        
        # Общая рекомендация
        winner = analysis.get("winner", {}).get("variant")
        if winner:
            recommendations.append(
                f"Рекомендуем использовать вариант {winner} как наиболее сбалансированный"
            )
        
        return recommendations
    
    def save_results(self, experiment_results: Dict):
        """Сохранение результатов эксперимента"""
        
        reports_dir = Path(__file__).parent.parent.parent / "reports" / "ab_tests"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем JSON
        json_file = reports_dir / f"{self.experiment_id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(experiment_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Сохраняем CSV для анализа
        csv_file = reports_dir / f"{self.experiment_id}.csv"
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Генерация визуализаций
        self._generate_visualizations(experiment_results, reports_dir)
        
        print(f"\nРезультаты сохранены:")
        print(f"  JSON: {json_file}")
        print(f"  CSV: {csv_file}")
    
    def _generate_visualizations(self, experiment_results: Dict, output_dir: Path):
        """Генерация графиков и визуализаций"""
        
        try:
            df = pd.DataFrame([r for r in self.results if r.get("success", False)])
            
            if df.empty:
                return
            
            # Настройка стиля
            plt.style.use('seaborn-v0_8-darkgrid')
            sns.set_palette("husl")
            
            # 1. Response time по вариантам
            plt.figure(figsize=(10, 6))
            sns.boxplot(data=df, x='variant', y='response_time')
            plt.title('Время ответа по вариантам промптов', fontsize=14, fontweight='bold')
            plt.xlabel('Вариант промпта', fontsize=12)
            plt.ylabel('Время ответа (секунды)', fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_dir / f"{self.experiment_id}_response_time.png", dpi=150)
            plt.close()
            
            # 2. Качество ответов
            plt.figure(figsize=(10, 6))
            df['quality'] = df['response'].apply(lambda x: x.get('quality_score', 0))
            sns.violinplot(data=df, x='variant', y='quality')
            plt.title('Качество ответов по вариантам промптов', fontsize=14, fontweight='bold')
            plt.xlabel('Вариант промпта', fontsize=12)
            plt.ylabel('Оценка качества (0-1)', fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_dir / f"{self.experiment_id}_quality.png", dpi=150)
            plt.close()
            
            # 3. Количество токенов
            plt.figure(figsize=(10, 6))
            df['tokens'] = df['metrics'].apply(lambda x: x.get('token_count', 0))
            sns.barplot(data=df, x='variant', y='tokens', estimator='mean', errorbar='sd')
            plt.title('Среднее количество токенов по вариантам', fontsize=14, fontweight='bold')
            plt.xlabel('Вариант промпта', fontsize=12)
            plt.ylabel('Токены', fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_dir / f"{self.experiment_id}_tokens.png", dpi=150)
            plt.close()
            
            # 4. Распределение оценок
            plt.figure(figsize=(12, 8))
            
            variants = df['variant'].unique()
            n_variants = len(variants)
            
            for i, variant in enumerate(variants, 1):
                plt.subplot(2, (n_variants + 1) // 2, i)
                variant_df = df[df['variant'] == variant]
                scores = variant_df['response'].apply(lambda x: x.get('score', 0))
                
                plt.hist(scores, bins=range(0, 12), alpha=0.7, edgecolor='black')
                plt.title(f'Вариант {variant}')
                plt.xlabel('Оценка')
                plt.ylabel('Частота')
                plt.xlim(0, 10)
            
            plt.suptitle('Распределение оценок по вариантам промптов', fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(output_dir / f"{self.experiment_id}_scores.png", dpi=150)
            plt.close()
            
            print(f"  Графики: {output_dir}/{self.experiment_id}_*.png")
            
        except Exception as e:
            print(f"Ошибка при генерации графиков: {e}")

async def run_ab_test_experiment():
    """Запуск полного A/B тестирования"""
    
    from ml.service.model_service import get_llm_service
    
    # Инициализация сервиса
    service = await get_llm_service()
    
    # Загрузка тестовых изображений
    test_images = []
    test_dir = Path(__file__).parent.parent.parent / "static" / "test_images"
    
    if test_dir.exists():
        clean_images = sorted(test_dir.glob("clear_*.jpg"))
        dirty_images = sorted(test_dir.glob("dirty_*.jpg"))
        
        for clean, dirty in zip(clean_images[:5], dirty_images[:5]):  # Первые 5 пар
            if clean.exists() and dirty.exists():
                test_images.append((str(clean), str(dirty)))
    
    if not test_images:
        print("No test images found")
        return
    
    # Создание и запуск эксперимента
    experiment = ABTestExperiment(service)
    results = await experiment.run_experiment(
        image_pairs=test_images,
        variants=["v1", "v2", "v3"],
        iterations=2,  # 2 итерации для каждого варианта
        user_id="ab_test_user"
    )
    
    # Вывод результатов
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ A/B ТЕСТИРОВАНИЯ")
    print("="*60)
    
    analysis = results.get("analysis", {})
    
    if analysis:
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        overall = analysis.get("overall", {})
        print(f"   Всего тестов: {overall.get('total_tests', 0)}")
        print(f"   Успешных: {overall.get('successful_tests', 0)}")
        print(f"   Успешность: {overall.get('success_rate', 0):.1%}")
        print(f"   Среднее время: {overall.get('avg_response_time', 0):.2f}с")
        print(f"   Среднее качество: {overall.get('avg_quality_score', 0):.2f}")
        
        print(f"\n🏆 ПОБЕДИТЕЛЬ: {analysis.get('winner', {}).get('variant', 'N/A')}")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        for rec in analysis.get("recommendations", []):
            print(f"   • {rec}")
        
        # Подробная статистика по вариантам
        print(f"\n📈 СТАТИСТИКА ПО ВАРИАНТАМ:")
        for variant, data in analysis.get("variants", {}).items():
            print(f"\n   {variant}:")
            print(f"     Тестов: {data.get('test_count', 0)}")
            print(f"     Среднее время: {data.get('response_time', {}).get('mean', 0):.2f}с")
            print(f"     Среднее качество: {data.get('quality', {}).get('mean', 0):.2f}")
            print(f"     Средние токены: {data.get('tokens', {}).get('mean', 0):.0f}")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_ab_test_experiment())