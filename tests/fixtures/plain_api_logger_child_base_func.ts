
interface Boundary {
    remote: (method_name:string, ...args:unknown[])=> Promise<unknown>
}


class Logger {
    private boundary: Boundary

    constructor(boundary:Boundary) {
        this.boundary = boundary
    }


    info(message:any): Promise<void> {
        return this.boundary.remote('logger.info', message) as Promise<void>
    }
    debug(message:any): Promise<void> {
        return this.boundary.remote('logger.debug', message) as Promise<void>
    }
    error(message:any): Promise<void> {
        return this.boundary.remote('logger.error', message) as Promise<void>
    }
}


class APIBridge {
    private boundary:Boundary

    public logger:Logger


    constructor(boundary:Boundary) {
        this.boundary = boundary

        this.logger = new Logger(boundary)

    }

    first_level(): Promise<void> {
        return this.boundary.remote('first_level') as Promise<void>
    }
}

export default APIBridge
