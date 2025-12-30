import { Cloud, CloudRain, Sun, CloudLightning, CloudSnow } from 'lucide-react'

function Clock({ time, date, weather }) {

    const getWeatherIcon = (code) => {
        // Basic mapping for Open-Meteo codes
        if (!code && code !== 0) return <Sun className="text-gray-400" size={48} />
        if (code <= 1) return <Sun className="text-yellow-400" size={48} />
        if (code <= 3) return <Cloud className="text-gray-400" size={48} />
        if (code <= 48) return <Cloud className="text-gray-400" size={48} />
        if (code <= 67) return <CloudRain className="text-blue-400" size={48} />
        if (code <= 77) return <CloudSnow className="text-white" size={48} />
        if (code <= 82) return <CloudRain className="text-blue-400" size={48} />
        if (code <= 86) return <CloudSnow className="text-white" size={48} />
        if (code <= 99) return <CloudLightning className="text-purple-400" size={48} />
        return <Sun size={48} />
    }

    return (
        <div className="glass-panel h-full flex flex-col p-6 justify-between relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-[-50px] right-[-50px] w-40 h-40 bg-blue-500/20 rounded-full blur-3xl"></div>

            <div>
                <div className="text-[7rem] font-black tracking-tighter leading-none bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                    {time || "--:--"}
                </div>
            </div>

            <div className="mt-4">
                <div className="text-4xl text-gray-300 font-light leading-none">
                    {date ? date.split(',')[0] : "..."}
                </div>
                <div className="text-2xl text-white font-bold leading-tight mt-1">
                    {date ? date.split(',')[1] : "Loading..."}
                </div>
            </div>

            <div className="flex items-center gap-4 mt-4 bg-white/5 p-4 rounded-xl border border-white/10">
                {weather ? (
                    <>
                        {getWeatherIcon(weather.code)}
                        <div>
                            <div className="text-3xl font-bold">{weather.temp}{weather.unit}</div>
                            <div className="text-xs text-gray-400 uppercase tracking-widest">{weather.location_name}</div>
                        </div>
                    </>
                ) : (
                    <div className="animate-pulse flex gap-4 w-full">
                        <div className="w-12 h-12 bg-white/10 rounded-full"></div>
                        <div className="flex-1">
                            <div className="h-6 w-20 bg-white/10 rounded mb-2"></div>
                            <div className="h-4 w-32 bg-white/10 rounded"></div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Clock
