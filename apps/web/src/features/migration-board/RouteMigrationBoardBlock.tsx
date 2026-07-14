"use client";

import { useQuery } from "@tanstack/react-query";
import { boardPostsQuery } from "../../entities/migration-board/api";
import { Link } from "../../i18n/navigation";
import { routes } from "../../shared/lib/routes";

export function RouteMigrationBoardBlock({ routeId }: { routeId: string }) {
  const posts = useQuery(boardPostsQuery({ route_id: routeId, limit: 3 }));
  const items = posts.data?.items ?? [];

  return (
    <div data-testid="route-migration-board-block">
      {items.length === 0 ? (
        <p className="text-c3 text-sm">
          Пока нет опубликованных записей по этому маршруту.
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
          href={`${routes.migrationBoardNew}?route_id=${routeId}`}
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          Создать запись с этим маршрутом
        </Link>
      </div>
    </div>
  );
}
