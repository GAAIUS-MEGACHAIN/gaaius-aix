import React from "react";
import styled from "styled-components";
import PeerLearningTab from "@/components/PeerLearningTab";

const PageContainer = styled.div`
  width: 100%;
  height: 100vh;
  display: flex;
`;

export default function PeerLearningPage() {
  return (
    <PageContainer>
      <PeerLearningTab />
    </PageContainer>
  );
}
