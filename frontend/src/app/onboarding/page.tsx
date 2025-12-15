import { OnboardingForm } from '@/components/onboarding/onboarding-form'

export default function OnboardingPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-2xl space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-foreground">
            Welcome to fLOKr
          </h1>
          <p className="mt-2 text-lg text-muted-foreground">
            Let's personalize your experience
          </p>
        </div>
        <OnboardingForm />
      </div>
    </div>
  )
}
