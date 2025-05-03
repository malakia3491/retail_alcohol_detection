import type { Shelving } from './shelf/shelving'
import type { Person } from './person_managment/person'
import { Planogram } from './shelf/planogram';

export interface PlanogramOrder {
    id?: string;
    author: Person;
    shelving_assignments: Record<string, Planogram[]>;
    create_date: Date;
    develop_date: Date;
    implementation_date: Date;
    shelvings: Shelving[];
    is_declined: boolean;
    status: string;
  }