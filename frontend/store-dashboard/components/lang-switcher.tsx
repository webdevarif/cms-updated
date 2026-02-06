import React from 'react'
import { useLocale } from 'next-intl'
import { usePathname, useRouter } from '@/i18n/navigation'
import { locales } from '@/i18n/request'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { Globe } from 'lucide-react'

const LangSwitcher = () => {
  const locale = useLocale()
  const pathname = usePathname()
  const router = useRouter()

  const handleLanguageChange = (newLocale: string) => {
    router.replace(pathname, { locale: newLocale })
  }

  const languageNames = {
    en: 'English',
    es: 'Español',
    fr: 'Français',
    bn: 'বাংলা'
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" className="relative">
          <Globe className="h-[1.2rem] w-[1.2rem]" />
          <span className="sr-only">Select language</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {locales.map((loc) => (
          <DropdownMenuItem 
            key={loc} 
            onClick={() => handleLanguageChange(loc)}
            className={locale === loc ? "bg-accent" : ""}
          >
            <span className="mr-2">
              {loc === 'en' && '🇺🇸'}
              {loc === 'es' && '🇪🇸'}
              {loc === 'fr' && '🇫🇷'}
              {loc === 'bn' && '🇧🇩'}
            </span>
            {languageNames[loc as keyof typeof languageNames] || loc.toUpperCase()}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default LangSwitcher