"use client";

import { useState } from "react";

/**
 * Главная страница MVP для роли Fullstack:
 * - поле для ввода учебного текста
 * - кнопка "Сгенерировать карточки"
 * - список сгенерированных карточек из backend (/ai/generate)
 */
export default function HomePage() {
  const [text, setText] = useState("");
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setError("");
    setCards([]);

    const trimmed = text.trim();
    if (!trimmed) {
      setError("Пожалуйста, введите текст для генерации.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/ai/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: trimmed }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `Ошибка запроса: ${response.status}`);
      }

      const data = await response.json();
      setCards(data.cards || []);
    } catch (e) {
      setError(e.message || "Неизвестная ошибка при генерации.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-2xl space-y-6">
        <h1 className="text-2xl font-bold text-center">
          Auto-Flashcards — MVP генератор карточек
        </h1>

        <p className="text-sm text-slate-300 text-center">
          Введите учебный текст, нажмите{" "}
          <span className="font-semibold">«Сгенерировать карточки»</span>, и
          backend (FastAPI) вернёт список простых карточек.
        </p>

        <div className="space-y-2">
          <label className="block text-sm font-medium">
            Учебный текст
          </label>
          <textarea
            className="w-full h-40 rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm outline-none focus:border-sky-500"
            placeholder="Например: FastAPI — это современный веб-фреймворк для Python..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full rounded-lg bg-sky-600 hover:bg-sky-500 disabled:bg-slate-600 py-2 text-sm font-semibold transition-colors"
        >
          {loading ? "Генерация..." : "Сгенерировать карточки"}
        </button>

        {error && (
          <div className="rounded-lg border border-red-600 bg-red-950/60 px-3 py-2 text-sm text-red-200">
            Ошибка: {error}
          </div>
        )}

        {cards.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold">Сгенерированные карточки</h2>
            <ul className="space-y-2">
              {cards.map((card, idx) => (
                <li
                  key={idx}
                  className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                >
                  <div className="font-medium mb-1">
                    Вопрос {idx + 1}:
                  </div>
                  <div className="mb-1">{card.question}</div>
                  <div className="text-slate-300">
                    <span className="font-medium">Ответ: </span>
                    {card.answer}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {cards.length === 0 && !error && !loading && (
          <p className="text-xs text-slate-500 text-center">
            Карточки ещё не сгенерированы. Введите текст и нажмите кнопку выше.
          </p>
        )}
      </div>
    </main>
  );
}
