import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Inbox from './pages/Inbox.jsx'
import Settings from './pages/Settings.jsx'
import './App.css'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Inbox />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App
