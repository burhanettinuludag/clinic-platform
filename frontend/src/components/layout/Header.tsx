'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import LanguageSwitcher from '@/components/common/LanguageSwitcher';
import { useAuth } from '@/context/AuthContext';
import { Menu, X, User, Brain, Activity, BookOpen, ShoppingBag, FileText, Newspaper, Mail, Shield } from 'lucide-react';
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

  const isAdmin = user?.role === 'admin';
  const dashboardPath =
    user?.role === 'doctor' || isAdmin
      ? '/doctor/dashboard'
      : user?.role === 'caregiver'
      ? '/caregiver/dashboard'
      : user?.role === 'relative'
      ? '/relative/dashboard'
      : '/patient/dashboard';

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

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1">
            <NavLink href="/" icon={<Activity className="w-4 h-4" />}>
              {t('nav.home')}
            </NavLink>
            <NavLink href="/education" icon={<BookOpen className="w-4 h-4" />}>
              {t('nav.education')}
            </NavLink>
            <NavLink href="/blog" icon={<FileText className="w-4 h-4" />}>
              {t('nav.blog')}
            </NavLink>
            <NavLink href="/news" icon={<Newspaper className="w-4 h-4" />}>
              {t('nav.news')}
            </NavLink>
            <NavLink href="/store" icon={<ShoppingBag className="w-4 h-4" />}>
              {t('nav.store')}
            </NavLink>
            <NavLink href="/contact" icon={<Mail className="w-4 h-4" />}>
              {t('nav.contact')}
            </NavLink>
          </nav>

          {/* Right Section */}
          <div className="hidden lg:flex items-center gap-3">
            <LanguageSwitcher />

            {user ? (
              <div className="flex items-center gap-3">
                {isAdmin && (
                  <a
                    href="/yonetim-7x9k/"
                    className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 hover:bg-amber-100 transition-all text-sm font-medium"
                  >
                    <Shield className="w-4 h-4" />
                    {t('nav.adminPanel')}
                  </a>
                )}
                <Link
                  href={dashboardPath}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-teal-50 border border-teal-200 text-gray-700 hover:bg-teal-100 transition-all"
                >
                  <div className="w-7 h-7 rounded-full bg-teal-600 flex items-center justify-center">
                    <User className="w-3.5 h-3.5 text-white" />
                  </div>
                  <span className="text-sm font-medium">{user.first_name}</span>
                </Link>
                <button
                  onClick={logout}
                  className="text-sm text-gray-400 hover:text-red-500 transition-colors"
                >
                  {t('common.logout')}
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/auth/login"
                  className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                >
                  {t('common.login')}
                </Link>
                <Link
                  href="/auth/register"
                  className="px-5 py-2 text-sm font-semibold text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors shadow-sm"
                >
                  {t('common.register')}
                </Link>
              </div>
            )}
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
              <MobileNavLink href="/" onClick={() => setMenuOpen(false)}>
                <Activity className="w-5 h-5 text-teal-600" />
                {t('nav.home')}
              </MobileNavLink>
              <MobileNavLink href="/education" onClick={() => setMenuOpen(false)}>
                <BookOpen className="w-5 h-5 text-teal-600" />
                {t('nav.education')}
              </MobileNavLink>
              <MobileNavLink href="/blog" onClick={() => setMenuOpen(false)}>
                <FileText className="w-5 h-5 text-teal-600" />
                {t('nav.blog')}
              </MobileNavLink>
              <MobileNavLink href="/news" onClick={() => setMenuOpen(false)}>
                <Newspaper className="w-5 h-5 text-teal-600" />
                {t('nav.news')}
              </MobileNavLink>
              <MobileNavLink href="/store" onClick={() => setMenuOpen(false)}>
                <ShoppingBag className="w-5 h-5 text-teal-600" />
                {t('nav.store')}
              </MobileNavLink>
              <MobileNavLink href="/contact" onClick={() => setMenuOpen(false)}>
                <Mail className="w-5 h-5 text-teal-600" />
                {t('nav.contact')}
              </MobileNavLink>

              <div className="my-2 border-t border-gray-100" />

              {user ? (
                <>
                  {isAdmin && (
                    <a
                      href="/yonetim-7x9k/"
                      className="flex items-center gap-3 px-4 py-3 text-amber-700 hover:bg-amber-50 rounded-lg transition-colors"
                    >
                      <Shield className="w-5 h-5" />
                      {t('nav.adminPanel')}
                    </a>
                  )}
                  <MobileNavLink href={dashboardPath} onClick={() => setMenuOpen(false)}>
                    <User className="w-5 h-5 text-teal-600" />
                    {t('nav.dashboard')}
                  </MobileNavLink>
                  <button
                    onClick={() => {
                      logout();
                      setMenuOpen(false);
                    }}
                    className="flex items-center gap-3 px-4 py-3 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                    {t('common.logout')}
                  </button>
                </>
              ) : (
                <>
                  <MobileNavLink href="/auth/login" onClick={() => setMenuOpen(false)}>
                    <User className="w-5 h-5 text-teal-600" />
                    {t('common.login')}
                  </MobileNavLink>
                  <Link
                    href="/auth/register"
                    onClick={() => setMenuOpen(false)}
                    className="mx-4 mt-2 py-2.5 text-center text-sm font-semibold text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
                  >
                    {t('common.register')}
                  </Link>
                </>
              )}

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
