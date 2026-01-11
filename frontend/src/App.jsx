import { useState, useEffect } from 'react'
import axios from 'axios'
import Clock from './components/Clock'
import SensorCard from './components/SensorCard'
import SettingsModal from './components/SettingsModal'
import GraphPanel from './components/GraphPanel'
import { Settings } from 'lucide-react'

function App() {
  const [data, setData] = useState(null)
  const [weather, setWeather] = useState(null)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [contextMenu, setContextMenu] = useState(null) // {x, y}

  const [history, setHistory] = useState([])

  const fetchData = async () => {
    try {
      const res = await axios.get('/api/status')
      const newData = res.data
      setData(newData)

      // Update History for Graph
      if (newData.sensors && newData.sensors.length >= 3) {
        const s1 = newData.sensors[0].temp
        const s2 = newData.sensors[1].temp
        const s3 = newData.sensors[2].temp
        const avg = (s1 + s2 + s3) / 3

        setHistory(prev => {
          const newPoint = {
            time: newData.time.split(' ')[0], // Just HH:mm:ss if possible, or usually API returns formatted time
            s1, s2, s3,
            avg: parseFloat(avg.toFixed(1))
          }
          const newHist = [...prev, newPoint]
          if (newHist.length > 360) newHist.shift() // Keep last 360 points (1 hour at 10s interval)
          return newHist
        })
      }
    } catch (e) {
      console.error("Status fetch error", e)
    }
  }

  // Smart polling for weather
  useEffect(() => {
    let timeoutId;

    const fetchWeatherLoop = async () => {
      let nextDelay = 15 * 60 * 1000; // 15 mins default

      try {
        const res = await axios.get('/api/weather')
        setWeather(res.data)

        // If offline or invalid, retry quickly
        if (!res.data || res.data.location_name === "Offline" || res.data.temp === "--") {
          console.log("Weather offline, retrying in 10s...");
          nextDelay = 10 * 1000;
        }
      } catch (e) {
        console.error("Weather fetch error", e)
        nextDelay = 10 * 1000; // Retry quickly on network error
      }

      timeoutId = setTimeout(fetchWeatherLoop, nextDelay);
    }

    // Start loops
    fetchData()
    fetchWeatherLoop()
    const statusInterval = setInterval(fetchData, 10000)

    return () => {
      clearInterval(statusInterval)
      clearTimeout(timeoutId)
    }
  }, [])

  const handleContextMenu = (e) => {
    e.preventDefault()
    setContextMenu({ x: e.clientX, y: e.clientY })
  }

  const closeContextMenu = () => setContextMenu(null)

  return (
    <div className="w-full h-screen flex text-white select-none bg-gradient-to-br from-slate-900 via-slate-800 to-black overflow-hidden"
      onContextMenu={handleContextMenu}
      onClick={closeContextMenu}>

      {/* Left Panel: Clock & Weather */}
      <div className="w-[350px] flex-none flex flex-col p-4 border-r border-white/5 z-20">
        <Clock
          time={data?.time}
          date={data?.date}
          weather={weather}
        />
      </div>

      {/* Middle Panel: Sensors */}
      <div className="w-[1120px] flex-none h-full p-4 border-r border-white/5 relative z-10 transition-all duration-300">
        <div className="grid grid-cols-5 gap-3 h-full">
          {data?.sensors.map((sensor, idx) => (
            <SensorCard key={sensor.id || idx} sensor={sensor} />
          ))}
          {/* Fill empty slots if less than 5 */}
          {!data && Array(5).fill(0).map((_, i) => (
            <div key={i} className="glass-panel animate-pulse opacity-50 h-full"></div>
          ))}
        </div>
      </div>

      {/* Right Panel: Graph */}
      <div className="w-[450px] flex-none h-full p-4 min-w-0 z-0">
        <GraphPanel
          history={history}
          sensorNames={data?.sensors?.slice(0, 3).map(s => s.name)}
        />
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <div style={{ top: contextMenu.y, left: contextMenu.x }}
          className="absolute bg-gray-900 border border-gray-700 rounded shadow-xl py-2 z-50 min-w-[150px]">
          <button
            className="w-full text-left px-4 py-2 hover:bg-gray-700 flex items-center gap-2"
            onClick={() => {
              setSettingsOpen(true)
              closeContextMenu()
            }}
          >
            <Settings size={16} /> Settings
          </button>
        </div>
      )}

      {/* Settings Modal */}
      {settingsOpen && <SettingsModal onClose={() => setSettingsOpen(false)} />}
    </div>
  )
}

export default App
