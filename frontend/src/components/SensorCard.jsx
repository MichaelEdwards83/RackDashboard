import { Thermometer } from 'lucide-react'

function SensorCard({ sensor }) {
    const getStatusColor = (status) => {
        switch (status) {
            case 'critical': return 'text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]'
            case 'warning': return 'text-orange-400 drop-shadow-[0_0_8px_rgba(2fb,146,60,0.5)]'
            default: return 'text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.3)]'
        }
    }

    const getBorderColor = (status) => {
        switch (status) {
            case 'critical': return 'border-red-500/50 bg-red-500/10'
            case 'warning': return 'border-orange-500/50 bg-orange-500/10'
            default: return 'border-glass-border'
        }
    }

    return (
        <div className={`glass-panel h-full flex flex-col items-center justify-center p-2 transition-all duration-500 ${getBorderColor(sensor.status)}`}>
            <h3 className="text-gray-400 text-2xl font-semibold uppercase tracking-wider mb-2 text-center w-full px-1 truncate">{sensor.name}</h3>

            <div className={`text-7xl font-bold flex items-start tabular-nums tracking-tighter justify-center ${getStatusColor(sensor.status)}`}>
                {sensor.temp}
                <span className="text-3xl mt-2 ml-1">°F</span>
            </div>

            {sensor.status === 'critical' && (
                <div className="mt-2 text-red-400 text-xs font-bold animate-pulse">CRITICAL</div>
            )}
        </div>
    )
}

export default SensorCard
