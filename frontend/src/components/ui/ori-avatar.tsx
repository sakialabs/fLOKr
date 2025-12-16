import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'

interface OriAvatarProps {
  size?: 'sm' | 'md' | 'lg'
  showBadge?: boolean
  isTyping?: boolean
  className?: string
}

const sizeMap = {
  sm: { container: 32, icon: 16 },
  md: { container: 40, icon: 20 },
  lg: { container: 56, icon: 28 }
}

export function OriAvatar({ 
  size = 'md', 
  showBadge = false,
  isTyping = false,
  className = '' 
}: OriAvatarProps) {
  const dimensions = sizeMap[size]
  
  return (
    <div className={`relative ${className}`}>
      {/* Main Avatar Circle */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        transition={{ type: "spring", stiffness: 300 }}
        className="relative"
        style={{ 
          width: dimensions.container, 
          height: dimensions.container 
        }}
      >
        {/* Base Circle - Orange (Oriole inspired) */}
        <div 
          className="absolute inset-0 rounded-full bg-gradient-to-br from-[#D97A5B] to-[#C26A52] shadow-lg overflow-hidden"
        >
          {/* Black Diagonal Stripes (Oriole pattern) */}
          <div className="absolute inset-0">
            <div className="absolute top-0 left-0 w-full h-full">
              {/* Stripe 1 */}
              <div 
                className="absolute bg-black/20 transform -rotate-45"
                style={{
                  width: '200%',
                  height: '15%',
                  top: '20%',
                  left: '-50%'
                }}
              />
              {/* Stripe 2 */}
              <div 
                className="absolute bg-black/15 transform -rotate-45"
                style={{
                  width: '200%',
                  height: '12%',
                  top: '45%',
                  left: '-50%'
                }}
              />
              {/* Stripe 3 */}
              <div 
                className="absolute bg-black/20 transform -rotate-45"
                style={{
                  width: '200%',
                  height: '15%',
                  top: '70%',
                  left: '-50%'
                }}
              />
            </div>
          </div>
          
          {/* White Accent Highlights */}
          <div className="absolute inset-0">
            <div 
              className="absolute bg-white/30 rounded-full blur-sm"
              style={{
                width: '40%',
                height: '40%',
                top: '10%',
                right: '15%'
              }}
            />
          </div>
          
          {/* Sparkle Icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <Sparkles 
              className="text-white drop-shadow-lg" 
              style={{ width: dimensions.icon, height: dimensions.icon }}
            />
          </div>
        </div>
        
        {/* Animated Glow Ring (when typing) */}
        {isTyping && (
          <motion.div
            animate={{
              scale: [1, 1.15, 1],
              opacity: [0.5, 0.8, 0.5],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="absolute inset-0 rounded-full border-2 border-[#D97A5B]/50"
          />
        )}
      </motion.div>
      
      {/* AI Badge */}
      {showBadge && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 500, delay: 0.2 }}
          className="absolute -bottom-1 -right-1 bg-gradient-to-br from-[#D97A5B] to-[#C26A52] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full shadow-md border-2 border-background"
        >
          AI
        </motion.div>
      )}
      
      {/* Online Status Indicator */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full bg-green-500 border-2 border-background shadow-sm"
      />
    </div>
  )
}
