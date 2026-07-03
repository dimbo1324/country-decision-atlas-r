import { LoginForm } from "../../features/auth";

export const dynamic = "force-dynamic";

export default function LoginPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Вход</p>
        <h1>Вход в аккаунт</h1>
      </header>
      <LoginForm />
    </div>
  );
}
