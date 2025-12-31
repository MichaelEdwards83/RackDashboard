import { useState, useEffect } from 'react'
import axios from 'axios'
import { X, Save, RefreshCw } from 'lucide-react'

function SettingsModal({ onClose }) {
    const [config, setConfig] = useState(null)
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [sensors, setSensors] = useState([])

    // Local state for form
    const [ntp, setNtp] = useState("")
    const [autoLoc, setAutoLoc] = useState(true)
    const [mock, setMock] = useState(false)
    const [brightness, setBrightness] = useState(255)

    // Per-sensor config state
    const [selectedScope, setSelectedScope] = useState("global") // "global" or sensor_id
    const [warn, setWarn] = useState(26)
    const [crit, setCrit] = useState(30)
    const [sensorName, setSensorName] = useState("")

    useEffect(() => {
        fetchConfig()
    }, [])

    const fetchConfig = async () => {
        try {
            // Fetch status to get sensor list
            const statusRes = await axios.get('/api/status')
            setSensors(statusRes.data.sensors || [])

            const res = await axios.get('/api/settings')
            const c = res.data
            setConfig(c)
            setNtp(c.ntp_server)
            setAutoLoc(c.location.auto)
            setMock(c.mock_mode)
            setBrightness(c.led_brightness !== undefined ? c.led_brightness : 255)

            // Init with global values
            const globalThr = c.temp_thresholds?.global || { warning: 26, critical: 30 }
            setWarn(globalThr.warning)
            setCrit(globalThr.critical)

        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    // Effect to update inputs when selection changes
    useEffect(() => {
        if (!config) return

        let target;
        if (selectedScope === "global") {
            target = config.temp_thresholds.global
            setSensorName("")
        } else {
            // Check if specific overrides exist, else default to global for UI consistency (or show placeholder)
            if (config.temp_thresholds.sensors && config.temp_thresholds.sensors[selectedScope]) {
                target = config.temp_thresholds.sensors[selectedScope]
            } else {
                target = config.temp_thresholds.global
            }
            // Get name
            const currentName = config.sensor_names ? config.sensor_names[selectedScope] : ""
            setSensorName(currentName || "")
        }

        setWarn(target.warning)
        setCrit(target.critical)
    }, [selectedScope, config])

    const handleSave = async () => {
        setSaving(true)
        try {
            await axios.post('/api/settings', {
                ntp_server: ntp,
                location_auto: autoLoc,
                threshold_warning: parseFloat(warn),
                threshold_critical: parseFloat(crit),
                sensor_id: selectedScope,
                sensor_name: selectedScope !== "global" ? sensorName : undefined,
                mock_mode: mock,
                led_brightness: parseInt(brightness)
            })
            // Update local config state to reflect changes without full reload
            const newConfig = { ...config }
            if (selectedScope === "global") {
                newConfig.temp_thresholds.global = { warning: parseFloat(warn), critical: parseFloat(crit) }
            } else {
                if (!newConfig.temp_thresholds.sensors) newConfig.temp_thresholds.sensors = {}
                newConfig.temp_thresholds.sensors[selectedScope] = { warning: parseFloat(warn), critical: parseFloat(crit) }

                // Update Name locally
                if (!newConfig.sensor_names) newConfig.sensor_names = {}
                newConfig.sensor_names[selectedScope] = sensorName
            }
            setConfig(newConfig)

            if (selectedScope === "global") onClose() // Only close on global save? Or maybe just toast. For now close.
            else alert(`Saved for ${selectedScope}`)

        } catch (e) {
            alert("Failed to save settings")
        } finally {
            setSaving(false)
        }
    }

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="glass-panel w-[500px] max-h-[90vh] overflow-y-auto p-6 text-left relative scrollbar-hide">
                <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-white sticky">
                    <X />
                </button>

                <h2 className="text-2xl font-bold mb-6">System Settings</h2>

                {loading ? (
                    <div className="flex justify-center p-10"><RefreshCw className="animate-spin" /></div>
                ) : (
                    <div className="space-y-6">
                        {/* Scope Selection */}
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1">Target</label>
                            <select
                                value={selectedScope}
                                onChange={(e) => setSelectedScope(e.target.value)}
                                className="w-full bg-black/30 border border-gray-600 rounded px-3 py-2 text-white outline-none focus:border-blue-500"
                            >
                                <option value="global">Global Defaults</option>
                                {sensors.map(s => (
                                    <option key={s.id} value={s.id}>{s.name} ({s.id})</option>
                                ))}
                            </select>
                        </div>

                        {selectedScope !== "global" && (
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-1">Sensor Name</label>
                                <input
                                    type="text"
                                    value={sensorName}
                                    onChange={e => setSensorName(e.target.value)}
                                    className="w-full bg-black/30 border border-gray-600 rounded px-3 py-2 text-white outline-none focus:border-blue-500"
                                    placeholder="e.g. CPU Temp"
                                />
                            </div>
                        )}

                        {/* Thresholds */}
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-3">Temperature Thresholds (°F)</label>
                            <div className="space-y-4">
                                <div className="flex items-center gap-4">
                                    <span className="w-20 text-orange-400 font-bold">Warning</span>
                                    <input
                                        type="range" min="50" max="120" step="1"
                                        value={warn} onChange={e => setWarn(e.target.value)}
                                        className="flex-1 accent-orange-500"
                                    />
                                    <span className="w-12 text-right">{warn}</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="w-20 text-red-500 font-bold">Critical</span>
                                    <input
                                        type="range" min="50" max="140" step="1"
                                        value={crit} onChange={e => setCrit(e.target.value)}
                                        className="flex-1 accent-red-500"
                                    />
                                    <span className="w-12 text-right">{crit}</span>
                                </div>
                            </div>
                        </div>

                        <hr className="border-white/10" />

                        {/* Global Only Settings */}
                        <div>
                            <h3 className="text-sm font-bold text-gray-500 uppercase mb-3">Global Configuration</h3>
                            {/* NTP */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-400 mb-1">NTP Server</label>
                                <input
                                    type="text"
                                    value={ntp}
                                    onChange={e => setNtp(e.target.value)}
                                    className="w-full bg-black/30 border border-gray-600 rounded px-3 py-2 text-white outline-none focus:border-blue-500"
                                    placeholder="pool.ntp.org"
                                />
                            </div>

                            {/* Location */}
                            <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                                <div>
                                    <div className="font-medium">Auto-Detect Location</div>
                                    <div className="text-xs text-gray-400">Use IP address for Weather</div>
                                </div>
                                <button
                                    onClick={() => setAutoLoc(!autoLoc)}
                                    className={`w-12 h-6 rounded-full transition-colors relative ${autoLoc ? 'bg-blue-600' : 'bg-gray-600'}`}
                                >
                                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${autoLoc ? 'left-7' : 'left-1'}`}></div>
                                </button>
                            </div>

                            <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg mt-2">
                                <div>
                                    <div className="font-medium">Mock Mode</div>
                                    <div className="text-xs text-gray-400">Simulate sensor data</div>
                                </div>
                                <button
                                    onClick={() => setMock(!mock)}
                                    disabled={!mock && config?.hw_failed}
                                    className={`w-12 h-6 rounded-full transition-colors relative ${mock ? 'bg-purple-600' : 'bg-gray-600'} ${(!mock && config?.hw_failed) ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${mock ? 'left-7' : 'left-1'}`}></div>
                                </button>
                            </div>

                            {/* LED Brightness */}
                            <div className="mt-4">
                                <label className="block text-sm font-medium text-gray-400 mb-1">LED Brightness ({brightness})</label>
                                <input
                                    type="range" min="0" max="255" step="5"
                                    value={brightness} onChange={e => setBrightness(e.target.value)}
                                    className="w-full accent-blue-500"
                                />
                            </div>
                        </div>

                        <button
                            onClick={handleSave}
                            disabled={saving}
                            className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-lg font-bold flex items-center justify-center gap-2 mt-4"
                        >
                            {saving ? <RefreshCw className="animate-spin" size={20} /> : <Save size={20} />}
                            Save
                        </button>
                    </div>
                )}
            </div>
        </div >
    )
}

export default SettingsModal
