import { Kicker } from "@country-decision-atlas/ui";
import { RegisterForm } from "../../../features/auth";

export const dynamic = "force-dynamic";

export default function RegisterPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Регистрация</Kicker>
        <h1 className="font-display text-4xl font-bold">Создать аккаунт</h1>
      </header>
      <RegisterForm />
    </div>
  );
}
