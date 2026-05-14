import { useEffect, useState } from 'react'
import { login as loginRequest, signup as signupRequest } from '../services/api'
import { AuthContext } from './auth-context'

const storageKey = 'sanjeevani_auth'

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState({ token: '', user: null })
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const hydrateAuth = () => {
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        try {
          const parsed = JSON.parse(saved)
          setAuth(parsed)
          if (parsed.token) {
            localStorage.setItem('sanjeevani_token', parsed.token)
          }
          return
        } catch {
          localStorage.removeItem(storageKey)
          localStorage.removeItem('sanjeevani_token')
        }
      }
      setAuth({ token: '', user: null })
    }

    hydrateAuth()

    const handleSessionExpired = () => {
      setAuth({ token: '', user: null })
    }

    window.addEventListener('sanjeevani:session-expired', handleSessionExpired)
    setReady(true)

    return () => {
      window.removeEventListener('sanjeevani:session-expired', handleSessionExpired)
    }
  }, [])

  const persist = (nextAuth) => {
    setAuth(nextAuth)
    localStorage.setItem(storageKey, JSON.stringify(nextAuth))
    localStorage.setItem('sanjeevani_token', nextAuth.token || '')
  }

  const login = async (payload) => {
    const data = await loginRequest(payload)
    persist({ token: data.access_token, user: { id: data.user_id, name: data.name, email: data.email } })
    return data
  }

  const signup = async (payload) => {
    const data = await signupRequest(payload)
    persist({ token: data.access_token, user: { id: data.user_id, name: data.name, email: data.email } })
    return data
  }

  const logout = () => {
    setAuth({ token: '', user: null })
    localStorage.removeItem(storageKey)
    localStorage.removeItem('sanjeevani_token')
  }

  return (
    <AuthContext.Provider value={{ ...auth, ready, login, signup, logout, isAuthenticated: Boolean(auth.token) }}>
      {children}
    </AuthContext.Provider>
  )
}
