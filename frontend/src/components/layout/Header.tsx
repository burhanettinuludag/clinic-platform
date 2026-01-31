'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import LanguageSwitcher from '@/components/common/LanguageSwitcher';
import { useAuth } from '@/context/AuthContext';
import { Menu, X, User, Brain, Activity, BookOpen, ShoppingBag, ChevronDown } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Header() {
  const t = useTranslations();
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const dashboardPath =
    user?.role === 'doctor' ? '/doctor/dashboard' : '/patient/dashboard';

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-slate-900/95 backdrop-blur-md shadow-lg shadow-cyan-500/10'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <Brain className="w-10 h-10 text-cyan-400 group-hover:text-cyan-300 transition-colors" />
              <div className="absolute inset-0 bg-cyan-400/20 blur-xl rounded-full group-hover:bg-cyan-300/30 transition-colors" />
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-white tracking-tight">
                Norosera
              </span>
              <span className="text-[10px] text-cyan-400/80 tracking-widest uppercase">
                Neurology Platform
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            <NavLink href="/" icon={<Activity className="w-4 h-4" />}>
              {t('nav.home')}
            </NavLink>
            <NavLink href="/education" icon={<BookOpen className="w-4 h-4" />}>
              {t('nav.education') || 'Egitim'}
            </NavLink>
            <NavLink href="/store" icon={<ShoppingBag className="w-4 h-4" />}>
              {t('nav.store')}
            </NavLink>
          </nav>

          {/* Right Section */}
          <div className="hidden md:flex items-center gap-4">
            <LanguageSwitcher />

            {user ? (
              <div className="flex items-center gap-3">
                <Link
                  href={dashboardPath}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/20 text-white hover:border-cyan-400/40 transition-all"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <span className="font-medium">{user.first_name}</span>
                </Link>
                <button
                  onClick={logout}
                  className="text-sm text-slate-400 hover:text-rose-400 transition-colors"
                >
                  {t('common.logout')}
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  href="/auth/login"
                  className="px-5 py-2.5 text-sm font-medium text-slate-300 hover:text-white transition-colors"
                >
                  {t('common.login')}
                </Link>
                <Link
                  href="/auth/register"
                  className="btn-primary text-sm"
                >
                  {t('common.register')}
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden py-4 border-t border-white/10 animate-fadeIn">
            <nav className="flex flex-col gap-2">
              <MobileNavLink href="/" onClick={() => setMenuOpen(false)}>
                <Activity className="w-5 h-5" />
                {t('nav.home')}
              </MobileNavLink>
              <MobileNavLink href="/education" onClick={() => setMenuOpen(false)}>
                <BookOpen className="w-5 h-5" />
                {t('nav.education') || 'Egitim'}
              </MobileNavLink>
              <MobileNavLink href="/store" onClick={() => setMenuOpen(false)}>
                <ShoppingBag className="w-5 h-5" />
                {t('nav.store')}
              </MobileNavLink>

              <div className="my-2 border-t border-white/10" />

              {user ? (
                <>
                  <MobileNavLink href={dashboardPath} onClick={() => setMenuOpen(false)}>
                    <User className="w-5 h-5" />
                    {t('nav.dashboard')}
                  </MobileNavLink>
                  <button
                    onClick={() => {
                      logout();
                      setMenuOpen(false);
                    }}
                    className="flex items-center gap-3 px-4 py-3 text-rose-400 hover:bg-rose-500/10 rounded-xl transition-colors"
                  >
                    <X className="w-5 h-5" />
                    {t('common.logout')}
                  </button>
                </>
              ) : (
                <>
                  <MobileNavLink href="/auth/login" onClick={() => setMenuOpen(false)}>
                    <User className="w-5 h-5" />
                    {t('common.login')}
                  </MobileNavLink>
                  <Link
                    href="/auth/register"
                    onClick={() => setMenuOpen(false)}
                    className="mx-4 mt-2 btn-primary text-center"
                  >
                    {t('common.register')}
                  </Link>
                </>
              )}

              <div className="px-4 pt-4">
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
      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
    >
      {icon && <span className="text-cyan-400">{icon}</span>}
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
      className="flex items-center gap-3 px-4 py-3 text-slate-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors"
    >
      {children}
    </Link>
  );
}
