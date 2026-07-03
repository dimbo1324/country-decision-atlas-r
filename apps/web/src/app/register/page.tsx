import { RegisterForm } from "../../features/auth";

export const dynamic = "force-dynamic";

export default function RegisterPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Регистрация</p>
        <h1>Создать аккаунт</h1>
      </header>
      <RegisterForm />
    </div>
  );
}
