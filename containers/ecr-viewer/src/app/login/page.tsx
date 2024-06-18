import { LoginForm } from "./LoginForm";

/**
 * @returns a login page
 */
export default async function LoginPage() {
  return (
    <section className="bg-ct-blue-600 min-h-screen pt-20">
      <div className="container mx-auto px-6 py-12 h-full flex justify-center items-center">
        <LoginForm />
      </div>
    </section>
  );
}
