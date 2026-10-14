import {Me} from "../api";
export function DashboardPage({me}:{me:Me}){
 return <section><div className="page-title"><div><small>OVERVIEW</small><h2>Welcome, {me.display_name}</h2><p>Track physical custody and digital processing in one linked workflow.</p></div><span className="chip">Private-first repository</span></div>
 <div className="metrics"><article><small>Physical identity</small><strong>1 : 1</strong><p>One physical file per case number</p></article><article><small>Scanner allocation</small><strong>Manual</strong><p>Explicit assignment per file</p></article><article><small>Publication gate</small><strong>Head approval</strong><p>Not public before confirmation</p></article></div>
 <h3>Your work areas</h3><div className="work-grid">{[
 ["Archive inventory","Register case identity, page counts and shelf location","ARCHIVE"],
 ["Batch dispatch","Build manifests and manually assign scanners","ARCHIVE"],
 ["Quality control","Verify both PDFs before private repository submission","QC_REPOSITORY"],
 ["Publication approval","Review private submissions and authorize publication","DEPARTMENT_HEAD"]
 ].filter(x=>me.roles.includes(x[2])||me.roles.includes("SYSTEM_ADMIN")||me.roles.includes("DEPARTMENT_HEAD")).map(x=><article key={x[0]}><b>{x[0]}</b><p>{x[1]}</p></article>)}</div>
 <div className="notice"><b>Security rule</b><p>Navigation visibility is not authorization. Every API operation is checked by Django.</p></div></section>;
}
