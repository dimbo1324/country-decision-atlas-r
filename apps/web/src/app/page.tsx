import Link from "next/link";
import { routes } from "../shared/lib/routes";

export default function Home() {
  return (
    <div className="homePage">
      <section className="intro">
        <p className="eyebrow">Country Decision Atlas</p>
        <h1>Relocation decisions with sourced country intelligence.</h1>
        <p>MVP countries: Russia and Uruguay.</p>
      </section>
      <div className="homeLinks">
        <Link href={routes.countries} className="homeLink">
          Go to Countries
        </Link>
        <Link href={routes.decision} className="homeLink">
          Go to Decision
        </Link>
      </div>
    </div>
  );
}
