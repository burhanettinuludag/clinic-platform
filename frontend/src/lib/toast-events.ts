type ToastType = 'success' | 'error' | 'warning' | 'info';

type ToastHandler = (type: ToastType, message: string) => void;

let handler: ToastHandler | null = null;

export function registerToastHandler(fn: ToastHandler) { handler = fn; }
export function unregisterToastHandler() { handler = null; }
export function emitToast(type: ToastType, message: string) { handler?.(type, message); }
