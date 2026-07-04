"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  listBoardPosts,
  type MigrationBoardPostListResponse,
} from "../../shared/api";
import { routes } from "../../shared/lib/routes";

export function CountryMigrationBoardBlock({
  countrySlug,
}: {
  countrySlug: string;
}) {
  const [data, setData] = useState<MigrationBoardPostListResponse | null>(null);

  useEffect(() => {
    let active = true;
    listBoardPosts({ destination_country: countrySlug, limit: 3 })
      .then((response) => {
        if (active) setData(response);
      })
      .catch(() => {
        if (active) setData({ items: [], total: 0, limit: 3, offset: 0 });
      });
    return () => {
      active = false;
    };
  }, [countrySlug]);

  const items = data?.items ?? [];

  return (
    <div data-testid="country-migration-board-block">
      {items.length === 0 ? (
        <p className="notice">
          Пока нет опубликованных записей для этой страны.
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
          href={`${routes.migrationBoard}?destination=${countrySlug}`}
          className="internalLink"
        >
          Все записи по направлению
        </Link>
      </div>
    </div>
  );
}
