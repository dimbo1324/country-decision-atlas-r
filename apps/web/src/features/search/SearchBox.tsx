"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { normalizeLocale } from "../../shared/lib/locale";

export function SearchBox() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));
  const [value, setValue] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = value.trim();
    if (!query) return;
    router.push(`/search?q=${encodeURIComponent(query)}&locale=${locale}`);
  }

  return (
    <form
      className="searchBox"
      role="search"
      onSubmit={handleSubmit}
      data-testid="search-box-form"
    >
      <input
        type="search"
        className="searchBoxInput"
        placeholder="Поиск по платформе…"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        aria-label="Поиск по платформе"
        data-testid="search-box-input"
      />
      <button type="submit" className="searchBoxSubmit" data-testid="search-box-submit">
        Найти
      </button>
    </form>
  );
}
