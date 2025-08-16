import dynamic from "next/dynamic";

const LeadGenForm = dynamic(() => import("../components/LeadGenForm"), {
  ssr: false,
});

export default function Home() {
  return <LeadGenForm />;
}
