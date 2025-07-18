export const roles = ['superadmin', 'manager', 'employee', 'tenant'];

export function hasAccess(userRole, resource) {
  // بررسی دسترسی نقش به resource
  return true;
} 