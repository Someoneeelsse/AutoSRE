import React, { useState, useEffect, useRef } from "react";

interface LogEntry {
  timestamp: string;
  ip: string;
  method: string;
  path: string;
  status: string;
  bytes: string;
  userAgent: string;
}

interface LogAnalysis {
  total_requests: number;
  status_code_distribution: Record<string, number>;
  error_count: number;
  success_rate: number;
  timestamp: string;
}

interface WebSocketMessage {
  type: "initial_data" | "update" | "error";
  logs?: string;
  analysis?: LogAnalysis;
  error_logs?: string[];
  message?: string;
  timestamp?: string;
  alerts?: any[];
}

const Dashboard: React.FC = () => {
  const [logs, setLogs] = useState<string>("");
  const [analysis, setAnalysis] = useState<LogAnalysis | null>(null);
  const [errorLogs, setErrorLogs] = useState<string[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected"
  >("disconnected");
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const heartbeatInterval = useRef<number | null>(null);
  const isComponentMounted = useRef(true);

  // Fetch system metrics
  const fetchSystemMetrics = async () => {
    try {
      const backendUrl =
        import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/metrics`);
      if (response.ok) {
        const metrics = await response.json();
        setSystemMetrics(metrics);
      }
    } catch (error) {
      console.error("Failed to fetch system metrics:", error);
    }
  };

  // Fetch metrics every 30 seconds
  useEffect(() => {
    fetchSystemMetrics();
    const interval = setInterval(fetchSystemMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const connectWebSocket = () => {
    // Prevent multiple connection attempts
    if (wsRef.current && wsRef.current.readyState === WebSocket.CONNECTING) {
      console.log("WebSocket: Already connecting, skipping new attempt.");
      return;
    }

    // Close existing connection if any
    if (wsRef.current) {
      console.log(
        "WebSocket: Closing existing connection before reconnecting."
      );
      wsRef.current.close(1000, "Reconnecting");
      wsRef.current = null;
    }

    setConnectionStatus("connecting");
    console.log("WebSocket: Attempting to connect...");

    // Get backend URL from environment variable or use default
    const backendUrl =
      import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
    const wsUrl = backendUrl.replace("http", "ws");

    // Connect to backend WebSocket
    const ws = new WebSocket(`${wsUrl}/ws`);

    ws.onopen = () => {
      console.log("WebSocket connected");
      setConnectionStatus("connected");
      reconnectAttempts.current = 0; // Reset reconnection attempts on successful connection

      // Start heartbeat to keep connection alive
      heartbeatInterval.current = window.setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000); // Send ping every 30 seconds
    };

    ws.onmessage = (event) => {
      console.log("WebSocket: Message received", event.data);
      try {
        const data: WebSocketMessage = JSON.parse(event.data);

        switch (data.type) {
          case "initial_data":
            if (data.logs) setLogs(data.logs);
            if (data.analysis) setAnalysis(data.analysis);
            if (data.error_logs) setErrorLogs(data.error_logs);
            if (data.alerts) setAlerts(data.alerts);
            setLastUpdated(new Date());
            break;

          case "update":
            if (data.analysis) setAnalysis(data.analysis);
            if (data.alerts) setAlerts(data.alerts);
            setLastUpdated(new Date());
            break;

          case "error":
            console.error("WebSocket error:", data.message);
            break;
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onclose = (event) => {
      console.log("WebSocket: Disconnected", event.code, event.reason);
      setConnectionStatus("disconnected");
      wsRef.current = null;

      // Clear heartbeat interval
      if (heartbeatInterval.current) {
        clearInterval(heartbeatInterval.current);
        heartbeatInterval.current = null;
      }

      // Don't reconnect for intentional closes (1000) or going away (1001)
      if (event.code === 1000 || event.code === 1001) {
        console.log("WebSocket: Intentional close, not reconnecting");
        return;
      }

      // Only attempt reconnection for unexpected disconnections and if component is still mounted
      if (
        reconnectAttempts.current < maxReconnectAttempts &&
        isComponentMounted.current
      ) {
        reconnectAttempts.current += 1;
        const delay = Math.min(5000 * reconnectAttempts.current, 30000); // Exponential backoff, max 30s

        console.log(
          `WebSocket: Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts}) in ${delay}ms...`
        );

        setTimeout(() => {
          // Only reconnect if we're still in disconnected state and component is mounted
          if (
            connectionStatus === "disconnected" &&
            !wsRef.current &&
            isComponentMounted.current
          ) {
            connectWebSocket();
          }
        }, delay);
      } else {
        console.error(
          "WebSocket: Max reconnection attempts reached, giving up"
        );
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket: Error event", error);
      // Don't set disconnected status here, let onclose handle it
    };

    wsRef.current = ws;
  };

  useEffect(() => {
    console.log("Dashboard mounted, connecting WebSocket...");

    // Set component as mounted
    isComponentMounted.current = true;

    // Clean up any existing connections first
    if (wsRef.current) {
      wsRef.current.close(1000, "Component remounting");
      wsRef.current = null;
    }

    // Reset reconnection attempts
    reconnectAttempts.current = 0;

    // Connect to WebSocket
    connectWebSocket();

    return () => {
      // Set component as unmounted
      isComponentMounted.current = false;

      // Clear heartbeat interval
      if (heartbeatInterval.current) {
        clearInterval(heartbeatInterval.current);
        heartbeatInterval.current = null;
      }

      if (wsRef.current) {
        console.log("Dashboard unmounting, closing WebSocket...");
        wsRef.current.close(1000, "Component unmounting");
        wsRef.current = null;
      }
    };
  }, []); // Empty dependency array to run only once

  const parseLogLine = (line: string): LogEntry | null => {
    const regex =
      /^(\S+) - - \[([^\]]+)\] "(\S+) (\S+) [^"]*" (\d+) (\d+) "([^"]*)" "([^"]*)"$/;
    const match = line.match(regex);

    if (match) {
      return {
        ip: match[1],
        timestamp: match[2],
        method: match[3],
        path: match[4],
        status: match[5],
        bytes: match[6],
        userAgent: match[8],
      };
    }
    return null;
  };

  const getStatusColor = (status: string) => {
    if (status.startsWith("2")) return "text-green-600";
    if (status.startsWith("3")) return "text-blue-600";
    if (status.startsWith("4")) return "text-yellow-600";
    if (status.startsWith("5")) return "text-red-600";
    return "text-gray-600";
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case "connected":
        return "text-green-600";
      case "connecting":
        return "text-yellow-600";
      case "disconnected":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case "connected":
        return "Connected";
      case "connecting":
        return "Connecting...";
      case "disconnected":
        return "Disconnected";
      default:
        return "Unknown";
    }
  };

  const recentLogs = logs
    .split("\n")
    .filter((line) => line.trim())
    .slice(-10)
    .reverse();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AutoSRE Dashboard
              </h1>
              <p className="text-gray-600">
                Real-time log monitoring and analysis
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div
                  className={`w-3 h-3 rounded-full ${getConnectionStatusColor().replace(
                    "text-",
                    "bg-"
                  )}`}
                ></div>
                <span
                  className={`text-sm font-medium ${getConnectionStatusColor()}`}
                >
                  {getConnectionStatusText()}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics Cards */}
        {analysis && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg
                    className="w-6 h-6 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Total Requests
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.total_requests}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <svg
                    className="w-6 h-6 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Success Rate
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.success_rate.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-red-100 rounded-lg">
                  <svg
                    className="w-6 h-6 text-red-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Errors</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.error_count}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <svg
                    className="w-6 h-6 text-purple-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Status Codes
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {Object.keys(analysis.status_code_distribution).length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Logs */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Logs</h3>
            </div>
            <div className="overflow-hidden">
              <div className="max-h-96 overflow-y-auto">
                {recentLogs.map((log, index) => {
                  const parsedLog = parseLogLine(log);
                  return (
                    <div
                      key={index}
                      className="px-6 py-3 border-b border-gray-100 hover:bg-gray-50"
                    >
                      {parsedLog ? (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-gray-900">
                              {parsedLog.method} {parsedLog.path}
                            </span>
                            <span
                              className={`text-sm font-semibold ${getStatusColor(
                                parsedLog.status
                              )}`}
                            >
                              {parsedLog.status}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500">
                            {parsedLog.timestamp} • {parsedLog.ip} •{" "}
                            {parsedLog.bytes} bytes
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm text-gray-600 font-mono">
                          {log}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* System Metrics */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                System Metrics
              </h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-6">
                {/* Uptime */}
                <div className="text-center">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <svg
                      className="w-8 h-8 text-blue-600 mx-auto mb-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <div className="text-2xl font-bold text-blue-600">
                      {systemMetrics?.uptime
                        ? `${systemMetrics.uptime.hours}h ${systemMetrics.uptime.minutes}m`
                        : "Loading..."}
                    </div>
                    <div className="text-sm text-gray-600">Uptime</div>
                  </div>
                </div>

                {/* Memory Usage */}
                <div className="text-center">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <svg
                      className="w-8 h-8 text-green-600 mx-auto mb-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                      />
                    </svg>
                    <div className="text-2xl font-bold text-green-600">
                      {systemMetrics?.memory
                        ? `${systemMetrics.memory.usage_percent.toFixed(1)}%`
                        : "Loading..."}
                    </div>
                    <div className="text-sm text-gray-600">Memory Usage</div>
                  </div>
                </div>

                {/* CPU Usage */}
                <div className="text-center">
                  <div className="p-3 bg-yellow-100 rounded-lg">
                    <svg
                      className="w-8 h-8 text-yellow-600 mx-auto mb-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                      />
                    </svg>
                    <div className="text-2xl font-bold text-yellow-600">
                      {systemMetrics?.cpu
                        ? `${systemMetrics.cpu.usage_percent.toFixed(1)}%`
                        : "Loading..."}
                    </div>
                    <div className="text-sm text-gray-600">CPU Usage</div>
                  </div>
                </div>

                {/* Active Connections */}
                <div className="text-center">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <svg
                      className="w-8 h-8 text-purple-600 mx-auto mb-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                      />
                    </svg>
                    <div className="text-2xl font-bold text-purple-600">
                      {systemMetrics?.active_connections || "Loading..."}
                    </div>
                    <div className="text-sm text-gray-600">
                      Active Connections
                    </div>
                  </div>
                </div>
              </div>

              {/* System Status */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                    <span className="text-sm font-medium text-gray-900">
                      All Systems Operational
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    Last updated: {new Date().toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Alerts Section */}
        {alerts.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Active Alerts ({alerts.length})
              </h3>
            </div>
            <div className="overflow-hidden">
              <div className="max-h-64 overflow-y-auto">
                {alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`px-6 py-4 border-b border-gray-100 ${
                      alert.type === "critical" ? "bg-red-50" : "bg-yellow-50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div
                          className={`w-3 h-3 rounded-full mr-3 ${
                            alert.type === "critical"
                              ? "bg-red-500"
                              : "bg-yellow-500"
                          }`}
                        ></div>
                        <div>
                          <div
                            className={`font-medium ${
                              alert.type === "critical"
                                ? "text-red-800"
                                : "text-yellow-800"
                            }`}
                          >
                            {alert.title}
                          </div>
                          <div
                            className={`text-sm ${
                              alert.type === "critical"
                                ? "text-red-600"
                                : "text-yellow-600"
                            }`}
                          >
                            {alert.message}
                          </div>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Error Logs */}
        {errorLogs.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Error Logs ({errorLogs.length})
              </h3>
            </div>
            <div className="overflow-hidden">
              <div className="max-h-64 overflow-y-auto">
                {errorLogs.map((errorLog, index) => (
                  <div
                    key={index}
                    className="px-6 py-3 border-b border-gray-100"
                  >
                    <div className="text-sm text-red-600 font-mono">
                      {errorLog}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Status Code Distribution */}
        {analysis && analysis.status_code_distribution && (
          <div className="mt-8 bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Status Code Distribution
              </h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {Object.entries(analysis.status_code_distribution).map(
                  ([status, count]) => (
                    <div key={status} className="text-center">
                      <div
                        className={`text-2xl font-bold ${getStatusColor(
                          status
                        )}`}
                      >
                        {status}
                      </div>
                      <div className="text-sm text-gray-600">
                        {count} requests
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
