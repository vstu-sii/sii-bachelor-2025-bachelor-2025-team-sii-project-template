class CleaningEvaluator:
    def __init__(self, test_dataset):
        self.test_dataset = test_dataset
        self.metrics = {}
    
    def calculate_accuracy(self, predictions, ground_truth):
        """Расчет точности предсказаний"""
        score_diff = abs(predictions - ground_truth)
        return 1 - (score_diff / 10)  # Нормализованная точность
    
    def evaluate_model(self, model):
        """Полная оценка модели"""
        results = []
        
        for image, true_score in self.test_dataset:
            prediction = model.assess_cleaning(image)
            accuracy = self.calculate_accuracy(prediction['score'], true_score)
            results.append({
                'image': image,
                'true_score': true_score,
                'predicted_score': prediction['score'],
                'accuracy': accuracy,
                'explanation': prediction['explanation']
            })
        
        return self.aggregate_metrics(results)
    
    def analyze_errors(self, results):
        """Анализ ошибок модели"""
        # Анализ паттернов ошибок, hallucinations
        pass