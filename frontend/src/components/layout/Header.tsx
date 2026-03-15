'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import LanguageSwitcher from '@/components/common/LanguageSwitcher';
import { Menu, X, Brain, Newspaper } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Header() {
  const t = useTranslations();
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-gray-100'
          : 'bg-white/80 backdrop-blur-sm'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 lg:h-18">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <Brain className="w-8 h-8 text-teal-600 group-hover:text-teal-500 transition-colors" />
            <div className="flex flex-col">
              <span className="text-xl font-bold text-gray-900 tracking-tight">
                Norosera
              </span>
              <span className="text-[9px] text-teal-600/80 tracking-widest uppercase -mt-0.5">
                {t('header.subtitle')}
              </span>
            </div>
          </Link>

          {/* Desktop Navigation - Launch Mode: sadece News */}
          <nav className="hidden lg:flex items-center gap-1">
            <NavLink href="/news" icon={<Newspaper className="w-4 h-4" />}>
              {t('nav.news')}
            </NavLink>
          </nav>

          {/* Right Section */}
          <div className="hidden lg:flex items-center gap-3">
            <LanguageSwitcher />

            {/* Auth buttons hidden - Launch Mode */}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="lg:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="lg:hidden py-4 border-t border-gray-100">
            <nav className="flex flex-col gap-1">
              <MobileNavLink href="/news" onClick={() => setMenuOpen(false)}>
                <Newspaper className="w-5 h-5 text-teal-600" />
                {t('nav.news')}
              </MobileNavLink>

              <div className="px-4 pt-3">
                <LanguageSwitcher />
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}

function NavLink({
  href,
  children,
  icon,
}: {
  href: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-gray-600 hover:text-teal-600 hover:bg-teal-50 rounded-lg transition-all"
    >
      {icon && <span className="text-gray-400">{icon}</span>}
      {children}
    </Link>
  );
}

function MobileNavLink({
  href,
  children,
  onClick,
}: {
  href: string;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:text-teal-600 hover:bg-teal-50 rounded-lg transition-colors"
    >
      {children}
    </Link>
  );
}
