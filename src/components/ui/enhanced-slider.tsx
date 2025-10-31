"use client"

import * as React from "react"
import * as SliderPrimitive from "@radix-ui/react-slider"
import { cn } from "@/lib/utils"

const EnhancedSlider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root>
>(({ className, ...props }, ref) => (
  <SliderPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex w-full touch-none select-none items-center group",
      className
    )}
    {...props}
  >
    <SliderPrimitive.Track className="relative h-1.5 w-full grow overflow-hidden rounded-full bg-slate-200 group-hover:h-2 group-hover:bg-slate-300 transition-all duration-200 ease-in-out">
      <SliderPrimitive.Range className="absolute h-full bg-gradient-to-r from-blue-500 to-purple-500 group-hover:from-blue-600 group-hover:to-purple-600 transition-all duration-200 ease-in-out" />
    </SliderPrimitive.Track>
    <SliderPrimitive.Thumb className="block h-5 w-5 rounded-full bg-blue-500 border-2 border-white shadow-lg shadow-blue-500/30 ring-offset-background transition-all duration-200 ease-in-out cursor-pointer hover:h-6 hover:w-6 hover:bg-blue-600 hover:shadow-xl hover:shadow-blue-500/40 hover:-translate-y-0.5 active:h-5.5 active:w-5.5 active:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50" />
  </SliderPrimitive.Root>
))
EnhancedSlider.displayName = SliderPrimitive.Root.displayName

export { EnhancedSlider }
