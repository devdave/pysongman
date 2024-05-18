 export type Identifier = string | number
export interface TagType {

    id: Identifier
    name: string
    value: string
}
export interface SongType {

    id: Identifier
    name: string
    artist: string
    size: number
    length_seconds: number
    tags: TagType[]
}

interface Boundary {
    remote: (method_name:string, ...args:unknown[])=> Promise<unknown>
}

class Logger {
    private boundary: Boundary

    constructor(boundary:Boundary) {
        this.boundary = boundary
    }

/*
Info logger
:param message:
:return:
*/

    info(message:string): Promise<void> {
        return this.boundary.remote('logger.info', message) as Promise<void>
    }

/*
Debug logger

:param message:
:return:
*/

    debug(message:string): Promise<void> {
        return this.boundary.remote('logger.debug', message) as Promise<void>
    }

/*
Error logger

:param message:
:return:
*/

    error(message:string): Promise<void> {
        return this.boundary.remote('logger.error', message) as Promise<void>
    }
}

class Songs {
    private boundary: Boundary

    constructor(boundary:Boundary) {
        this.boundary = boundary
    }

    list(page:number, limit:number = 100):Promise<SongType[]> {
        return this.boundary.remote('songs.list', page, limit) as Promise<SongType[]>
    }
    get(song_id:number):Promise<SongType> {
        return this.boundary.remote('songs.get', song_id) as Promise<SongType>
    }
    play(song_id:number):Promise<SongType> {
        return this.boundary.remote('songs.play', song_id) as Promise<SongType>
    }
    stop(): Promise<void> {
        return this.boundary.remote('songs.stop') as Promise<void>
    }
}

class APIBridge {
    private boundary:Boundary

    public logger:Logger

    public songs:Songs

    constructor(boundary:Boundary) {
        this.boundary = boundary

        this.logger = new Logger(boundary)

        this.songs = new Songs(boundary)
    }
}

export default APIBridge
