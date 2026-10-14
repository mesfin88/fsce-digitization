const API=import.meta.env.VITE_API_BASE_URL||"http://127.0.0.1:8000/api";
export async function api<T>(path:string,init:RequestInit={}):Promise<T>{
 const r=await fetch(`${API}${path}`,{credentials:"include",headers:{"Content-Type":"application/json",...(init.headers||{})},...init});
 if(!r.ok) throw new Error((await r.text())||`Request failed ${r.status}`);
 if(r.status===204)return undefined as T; return r.json() as Promise<T>;
}
export type Me={id:number;username:string;display_name:string;roles:string[]};
export type Location={id:number;code:string;description:string;active:boolean};
export type PhysicalFile={id:number;case:number;case_number:string;location:number;location_code:string;inventory_page_count:number;status:string};
export type BatchItem={id:number;physical_file:number;case_number:string;assigned_scanner:number;scanner_username:string;inventory_page_count_snapshot:number};
export type Batch={id:number;batch_number:string;source_location:number;status:string;items:BatchItem[];exception_notes:string};
export type Submission={id:number;physical_file:number;case_number:string;qc:number;dspace_uuid:string;status:string;is_private:boolean;submitted_at:string};
