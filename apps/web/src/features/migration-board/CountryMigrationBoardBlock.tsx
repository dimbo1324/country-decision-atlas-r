"use client";

import { useQuery } from "@tanstack/react-query";
import { boardPostsQuery } from "../../entities/migration-board/api";
import { Link } from "../../i18n/navigation";
import { routes } from "../../shared/lib/routes";

export function CountryMigrationBoardBlock({
  countrySlug,
}: {
  countrySlug: string;
}) {
  const posts = useQuery(
    boardPostsQuery({ destination_country: countrySlug, limit: 3 }),
  );
  const items = posts.data?.items ?? [];

  return (
    <div data-testid="country-migration-board-block">
      {items.length === 0 ? (
        <p className="text-c3 text-sm">
          Пока нет опубликованных записей для этой страны.
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((post) => (
            <Link
              href={routes.migrationBoardPost(post.id)}
              key={post.id}
              className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
            >
              {post.title}
            </Link>
          ))}
        </div>
      )}
      <div className="mt-3">
        <Link
          href={`${routes.migrationBoard}?destination=${countrySlug}`}
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          Все записи по направлению
        </Link>
      </div>
    </div>
  );
}
