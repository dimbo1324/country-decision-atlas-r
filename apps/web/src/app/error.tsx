"use client";

import { useEffect } from "react";

type Props = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function GlobalError({ error, reset }: Props) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Ошибка</p>
        <h1>Что-то пошло не так</h1>
      </header>
      <p>Произошла непредвиденная ошибка. Попробуйте обновить страницу.</p>
      <button
        onClick={reset}
        className="clearButton"
      >
        Попробовать снова
      </button>
    </div>
  );
}
