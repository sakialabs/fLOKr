export interface PasswordStrength {
  score: number // 0-5 (based on requirements + bonus)
  feedback: string[]
  label: 'Weak' | 'Fair' | 'Good' | 'Strong' | 'Very Strong'
  color: string
  isValid: boolean // true if all requirements met
}

export function validatePassword(password: string): PasswordStrength {
  let score = 0
  const feedback: string[] = []

  // Length check (required)
  const hasLength = password.length >= 8
  if (!hasLength) {
    feedback.push('At least 8 characters')
  } else {
    score += 1
  }

  // Uppercase check (required)
  const hasUppercase = /[A-Z]/.test(password)
  if (!hasUppercase) {
    feedback.push('One uppercase letter')
  } else {
    score += 1
  }

  // Lowercase check (required)
  const hasLowercase = /[a-z]/.test(password)
  if (!hasLowercase) {
    feedback.push('One lowercase letter')
  } else {
    score += 1
  }

  // Number check (required)
  const hasNumber = /\d/.test(password)
  if (!hasNumber) {
    feedback.push('One number')
  } else {
    score += 1
  }

  // Special character check (required)
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password)
  if (!hasSpecial) {
    feedback.push('One special character (!@#$%^&*)')
  } else {
    score += 1
  }

  // Bonus point for length >= 12
  if (password.length >= 12) {
    score += 1
  }

  // All requirements met
  const isValid = hasLength && hasUppercase && hasLowercase && hasNumber && hasSpecial

  // Determine label and color based on requirements met
  let label: PasswordStrength['label']
  let color: string

  if (score <= 1) {
    label = 'Weak'
    color = 'bg-red-500'
  } else if (score <= 3) {
    label = 'Fair'
    color = 'bg-orange-500'
  } else if (score === 4) {
    label = 'Good'
    color = 'bg-yellow-500'
  } else if (score === 5) {
    label = 'Strong'
    color = 'bg-green-500'
  } else {
    label = 'Very Strong'
    color = 'bg-emerald-500'
  }

  return { score, feedback, label, color, isValid }
}
