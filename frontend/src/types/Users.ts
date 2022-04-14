import Role from './Role';

interface User {
    id: number;
    firstName: string;
    lastName: string;
    department: string;
    defaultPathwayId: number;
    lastAccess?: Date;
    roles: Role[];
    token: string;
    isAdmin: boolean;
}

export default User;
