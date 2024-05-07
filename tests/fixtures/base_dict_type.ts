export interface Base {

    created_on: string
    updated_on: string
}
export interface Person extends Base {

    name: string
    age: number
}
