import { useUserStore } from '@/stores/user'

export function useAuth() {
  const userStore = useUserStore()
  return {
    isLoggedIn: userStore.isLoggedIn,
    username: userStore.username,
    logout: userStore.logout,
  }
}
