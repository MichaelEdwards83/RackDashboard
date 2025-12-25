import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

function GraphPanel({ history, sensorNames = ["Probe 1", "Probe 2", "Probe 3"] }) {
    // history is array of { time: 'HH:mm:ss', s1: val, s2: val, s3: val, avg: val }

    return (
        <div className="glass-panel h-full p-4 flex flex-col">
            <h2 className="text-gray-400 text-xs font-semibold tracking-widest uppercase">RACK TEMPERATURE</h2>

            <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                        <XAxis
                            dataKey="time"
                            stroke="#ffffff50"
                            tick={{ fontSize: 10 }}
                            interval="preserveStartEnd"
                            minTickGap={30}
                        />
                        <YAxis
                            stroke="#ffffff50"
                            tick={{ fontSize: 10 }}
                            domain={['auto', 'auto']}
                            width={30}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#000000cc', border: '1px solid #ffffff20', borderRadius: '8px', color: '#fff' }}
                            itemStyle={{ fontSize: '12px' }}
                        />

                        {/* Sensor 1 - Blue */}
                        <Line type="monotone" dataKey="s1" stroke="#3b82f6" strokeWidth={2} dot={false} name={sensorNames[0]} />
                        {/* Sensor 2 - Emerald */}
                        <Line type="monotone" dataKey="s2" stroke="#10b981" strokeWidth={2} dot={false} name={sensorNames[1]} />
                        {/* Sensor 3 - Amber */}
                        <Line type="monotone" dataKey="s3" stroke="#f59e0b" strokeWidth={2} dot={false} name={sensorNames[2]} />

                        {/* Average - White/Thick */}
                        <Line type="monotone" dataKey="avg" stroke="#ffffff" strokeWidth={3} dot={false} strokeDasharray="5 5" name="Average" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Legend / Stats */}
            <div className="flex justify-around mt-2 text-xs text-gray-400">
                <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-blue-500"></div> {sensorNames[0]}</span>
                <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> {sensorNames[1]}</span>
                <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-amber-500"></div> {sensorNames[2]}</span>
                <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-white"></div> Avg</span>
            </div>
        </div>
    )
}

export default GraphPanel
