import {FormEvent,useEffect,useState} from "react";
import {api,Location,PhysicalFile} from "../api";
export function InventoryPage(){
 const [locs,setLocs]=useState<Location[]>([]),[files,setFiles]=useState<PhysicalFile[]>([]);
 const [caseNo,setCaseNo]=useState(""),[pages,setPages]=useState("0"),[loc,setLoc]=useState(""),[desc,setDesc]=useState(""),[msg,setMsg]=useState("");
 const refresh=()=>Promise.all([api<Location[]>("/archive-locations/"),api<PhysicalFile[]>("/physical-files/")]).then(([l,f])=>{setLocs(l);setFiles(f);if(!loc&&l[0])setLoc(String(l[0].id));}).catch(e=>setMsg(e.message));
 useEffect(()=>{void refresh();},[]);
 async function submit(e:FormEvent){e.preventDefault();try{const c=await api<{id:number}>("/cases/",{method:"POST",body:JSON.stringify({case_number:caseNo,description:desc})});
 await api("/physical-files/",{method:"POST",body:JSON.stringify({case:c.id,location:Number(loc),inventory_page_count:Number(pages),condition_notes:""})});
 setCaseNo("");setDesc("");setPages("0");setMsg("Physical file registered.");await refresh();}catch(e){setMsg(e instanceof Error?e.message:"Save failed");}}
 return <section><div className="page-title"><div><small>ARCHIVE OPERATIONS</small><h2>Physical file inventory</h2><p>Register one physical file for each unique case number.</p></div></div>
 <form className="panel grid-form" onSubmit={submit}><label>Case number<input required value={caseNo} onChange={e=>setCaseNo(e.target.value)} placeholder="00/0001/205642"/></label><label>Physical page count<input required type="number" min="0" value={pages} onChange={e=>setPages(e.target.value)}/></label><label>Shelf location<select required value={loc} onChange={e=>setLoc(e.target.value)}>{locs.map(l=><option key={l.id} value={l.id}>{l.code}</option>)}</select></label><label>Description<input value={desc} onChange={e=>setDesc(e.target.value)}/></label><button className="primary">Register file</button></form>
 {msg&&<p className="message">{msg}</p>}<div className="panel table-wrap"><h3>Registered physical files</h3><table><thead><tr><th>Case number</th><th>Shelf</th><th>Pages</th><th>Status</th></tr></thead><tbody>{files.map(f=><tr key={f.id}><td>{f.case_number}</td><td>{f.location_code}</td><td>{f.inventory_page_count}</td><td>{f.status}</td></tr>)}</tbody></table></div></section>;
}
