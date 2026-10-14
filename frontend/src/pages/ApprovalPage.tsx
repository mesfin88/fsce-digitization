import {useEffect,useState} from "react";
import {api,Submission} from "../api";
export function ApprovalPage({mode}:{mode:"list"|"approve"}){
 const [items,setItems]=useState<Submission[]>([]),[msg,setMsg]=useState("");
 const refresh=()=>api<Submission[]>("/submissions/").then(setItems).catch(e=>setMsg(e.message));
 useEffect(()=>{void refresh();},[]);
 async function approve(id:number){try{await api(`/submissions/${id}/approve-publication/`,{method:"POST",body:JSON.stringify({})});setMsg("DSpace confirmed publication.");await refresh();}catch(e){setMsg(e instanceof Error?e.message:"Approval failed");}}
 const visible=mode==="approve"?items.filter(i=>i.status==="PRIVATE"&&i.is_private):items;
 return <section><div className="page-title"><div><small>{mode==="approve"?"FINAL AUTHORIZATION":"REPOSITORY WORKFLOW"}</small><h2>{mode==="approve"?"Publication approval":"Private submissions"}</h2><p>{mode==="approve"?"Only the Digitization Department Head can approve publication.":"Items remain private until final approval is confirmed by DSpace."}</p></div></div>{msg&&<p className="message">{msg}</p>}
 <div className="panel table-wrap"><h3>{mode==="approve"?"Awaiting Head approval":"Repository submissions"}</h3><table><thead><tr><th>Case</th><th>DSpace UUID</th><th>Status</th><th>Visibility</th>{mode==="approve"&&<th>Action</th>}</tr></thead><tbody>{visible.map(i=><tr key={i.id}><td>{i.case_number}</td><td>{i.dspace_uuid||"Not connected"}</td><td>{i.status}</td><td>{i.is_private?"Private":"Public"}</td>{mode==="approve"&&<td><button disabled={!i.is_private||i.status!=="PRIVATE"} onClick={()=>void approve(i.id)}>Approve & publish</button></td>}</tr>)}</tbody></table></div>
 <div className="notice"><b>Authorization enforced by API</b><p>A system administrator without the Department Head role cannot approve publication. The API also requires passed QC and confirmation from DSpace.</p></div></section>;
}
