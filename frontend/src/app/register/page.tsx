import { RegisterForm } from '@/components/auth/register-form'
import { Logo } from '@/components/ui/logo'

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-2xl space-y-8">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <Logo size={64} className="text-primary" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-foreground">
            Join fLOKr
          </h1>
          <p className="mt-2 text-muted-foreground">
            Connect with your community and access resources with dignity
          </p>
        </div>
        <RegisterForm />
      </div>
    </div>
  )
}
