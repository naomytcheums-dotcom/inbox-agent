import { NavLink } from 'react-router-dom'
import './Layout.css'

function Layout({ children }) {
  return (
    <div className="app-shell">
      <header className="topnav">
        <div className="topnav-inner">
          <div className="brand">Inbox Agent</div>
          <nav className="topnav-links">
            <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
              Inbox
            </NavLink>
            <NavLink to="/settings" className={({ isActive }) => (isActive ? 'active' : '')}>
              Settings
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="app-main">{children}</main>
    </div>
  )
}

export default Layout
