"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  listBoardPosts,
  type MigrationBoardPostListResponse,
} from "../../shared/api";
import { routes } from "../../shared/lib/routes";

export function RouteMigrationBoardBlock({ routeId }: { routeId: string }) {
  const [data, setData] = useState<MigrationBoardPostListResponse | null>(null);

  useEffect(() => {
    let active = true;
    listBoardPosts({ route_id: routeId, limit: 3 })
      .then((response) => {
        if (active) setData(response);
      })
      .catch(() => {
        if (active) setData({ items: [], total: 0, limit: 3, offset: 0 });
      });
    return () => {
      active = false;
    };
  }, [routeId]);

  const items = data?.items ?? [];

  return (
    <div data-testid="route-migration-board-block">
      {items.length === 0 ? (
        <p className="notice">
          Пока нет опубликованных записей по этому маршруту.
        </p>
      ) : (
        <div className="sectionStack">
          {items.map((post) => (
            <Link
              className="internalLink"
              href={routes.migrationBoardPost(post.id)}
              key={post.id}
            >
              {post.title}
            </Link>
          ))}
        </div>
      )}
      <div className="entityLinkRow">
        <Link
          href={`${routes.migrationBoardNew}?route_id=${routeId}`}
          className="internalLink"
        >
          Создать запись с этим маршрутом
        </Link>
      </div>
    </div>
  );
}
