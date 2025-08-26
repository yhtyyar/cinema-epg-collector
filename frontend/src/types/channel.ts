export type ChannelItem = {
  id: string
  count: number
}

export type ChannelsResponse = {
  channels: ChannelItem[]
}

export type ChannelEntry = {
  id?: string
  title?: string
  desc?: string
  timestart?: number
  timestop?: number
  preview?: string
  our_id?: string
  kinopoisk?: Record<string, any>
  poster_url?: string
  poster_local?: string
  poster_static?: string
  poster_source?: string
}

export type ChannelData = {
  our_id: string
  count: number
  items: ChannelEntry[]
}
