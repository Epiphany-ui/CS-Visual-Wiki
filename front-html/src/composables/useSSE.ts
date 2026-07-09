import type { SSETaskEvent, SSEDoneEvent } from '@/types/api'

type SSECallback = (data: SSETaskEvent | SSEDoneEvent) => void

const MAX_RETRIES = 3
const RETRY_DELAY_MS = 2000

export function useSSE() {
  let eventSource: EventSource | null = null
  let retryCount = 0
  let retryTimer: ReturnType<typeof setTimeout> | null = null
  // 保存回调，重连时复用
  let savedOnMessage: SSECallback | null = null
  let savedOnError: ((err: Event) => void) | null = null
  let savedTaskId: string | null = null

  function connect(taskId: string, onMessage: SSECallback, onError?: (err: Event) => void) {
    // 清理上一次的连接
    disconnect()

    savedTaskId = taskId
    savedOnMessage = onMessage
    savedOnError = onError
    retryCount = 0

    _doConnect(taskId, onMessage, onError)
  }

  function _doConnect(taskId: string, onMessage: SSECallback, onError?: (err: Event) => void) {
    const url = `http://localhost:8000/api/tasks/${taskId}/stream`
    eventSource = new EventSource(url)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)

        // 如果收到终态事件，停止重试
        if (data.type === 'done' || data.state === 'SUCCESS' || data.state === 'FAILURE') {
          retryCount = MAX_RETRIES // 阻止后续重连
        }
      } catch (e) {
        console.warn('SSE parse error:', e)
      }
    }

    eventSource.onerror = () => {
      // 已收到终态 → 这是服务端关闭连接触发的 onerror，不重连
      if (retryCount >= MAX_RETRIES) {
        onError?.(new Event('done'))
        return
      }

      console.error(`SSE error (retry ${retryCount}/${MAX_RETRIES})`)
      onError?.(new Event('error'))

      if (eventSource) {
        eventSource.close()
        eventSource = null
      }

      if (savedTaskId && savedOnMessage) {
        retryCount++
        console.log(`SSE reconnecting in ${RETRY_DELAY_MS}ms (attempt ${retryCount}/${MAX_RETRIES})...`)
        retryTimer = setTimeout(() => {
          if (savedTaskId && savedOnMessage) {
            _doConnect(savedTaskId, savedOnMessage, savedOnError || undefined)
          }
        }, RETRY_DELAY_MS)
      }
    }
  }

  function disconnect() {
    if (retryTimer) {
      clearTimeout(retryTimer)
      retryTimer = null
    }
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    retryCount = 0
    savedTaskId = null
    savedOnMessage = null
    savedOnError = null
  }

  return { connect, disconnect }
}
