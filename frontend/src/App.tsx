import {useEffect,useState} from "react";
import {NavLink,Navigate,Route,Routes} from "react-router-dom";
import {api,Me} from "./api";
import {DashboardPage} from "./pages/DashboardPage";
import {InventoryPage} from "./pages/InventoryPage";
import {BatchesPage} from "./pages/BatchesPage";
import {QualityPage} from "./pages/QualityPage";
import {ApprovalPage} from "./pages/ApprovalPage";
const nav=[
 {to:"/dashboard",label:"Dashboard",roles:[]},
 {to:"/archive/inventory",label:"Archive inventory",roles:["ARCHIVE","DEPARTMENT_HEAD","SYSTEM_ADMIN"]},
 {to:"/archive/batches",label:"Batches & dispatch",roles:["ARCHIVE","DEPARTMENT_HEAD","SYSTEM_ADMIN"]},
 {to:"/quality-control",label:"Quality control",roles:["QC_REPOSITORY"]},
 {to:"/repository/submissions",label:"Private submissions",roles:["QC_REPOSITORY","DEPARTMENT_HEAD"]},
 {to:"/publication/approval",label:"Publication approval",roles:["DEPARTMENT_HEAD"]}
];
export default function App(){
 const [me,setMe]=useState<Me|null>(null),[error,setError]=useState(""),[collapsed,setCollapsed]=useState(false);
 useEffect(()=>{api<Me>("/me/").then(setMe).catch(()=>setError("Sign in using Django at /api-auth/login/, then refresh this page."));},[]);
 if(error)return <div className="login-state"><h1>FSCE Digitization</h1><p>{error}</p><a href="http://127.0.0.1:8000/api-auth/login/">Open sign-in</a></div>;
 if(!me)return <div className="loading">Loading workspace…</div>;
 const items=nav.filter(n=>!n.roles.length||me.roles.some(r=>n.roles.includes(r)));
 return <div className={`shell ${collapsed?"collapsed":""}`}><aside className="sidebar">
  <div className="brand"><b>FS</b>{!collapsed&&<div><strong>Federal Supreme Court</strong><small>Digitization system</small></div>}</div>
  <button className="collapse" onClick={()=>setCollapsed(!collapsed)}>{collapsed?"›":"‹"}</button>
  <nav>{items.map(n=><NavLink key={n.to} to={n.to} title={collapsed?n.label:undefined} className={({isActive})=>isActive?"nav active":"nav"}><span>•</span>{!collapsed&&n.label}</NavLink>)}</nav>
  {!collapsed&&<div className="sidebar-user"><small>Signed in</small><b>{me.display_name}</b><small>{me.roles.join(" · ")||"No roles assigned"}</small></div>}
 </aside><main><header><div><small>COURT RECORDS OPERATIONS</small><h1>Digitization workspace</h1></div><span className="user">{me.display_name}</span></header><div className="content"><Routes>
  <Route path="/" element={<Navigate to="/dashboard" replace/>}/><Route path="/dashboard" element={<DashboardPage me={me}/>}/>
  <Route path="/archive/inventory" element={<InventoryPage/>}/><Route path="/archive/batches" element={<BatchesPage/>}/>
  <Route path="/quality-control" element={<QualityPage/>}/><Route path="/repository/submissions" element={<ApprovalPage mode="list"/>}/>
  <Route path="/publication/approval" element={<ApprovalPage mode="approve"/>}/><Route path="*" element={<Navigate to="/dashboard" replace/>}/>
 </Routes></div></main></div>;
}
