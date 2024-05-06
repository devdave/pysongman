
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

    info(message:any): Promise<void> {
        return this.boundary.remote('logger.info', message) as Promise<void>
    }

/*
Debug logger

:param message:
:return:
*/

    debug(message:any): Promise<void> {
        return this.boundary.remote('logger.debug', message) as Promise<void>
    }

/*
Error logger

:param message:
:return:
*/

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

    test(): Promise<void> {
        return this.boundary.remote('test') as Promise<void>
    }
}

export default APIBridge
