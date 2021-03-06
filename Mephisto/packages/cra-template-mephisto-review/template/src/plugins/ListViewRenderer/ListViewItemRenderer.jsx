import React from "react";
import { H6 } from "@blueprintjs/core";

function ListViewItemRenderer({ item }) {
  return (
    <>
      <pre>{JSON.stringify(item && item.data)}</pre>
      <H6>
        <b>ID: {item && item.id}</b>
      </H6>
    </>
  );
}

export default ListViewItemRenderer;
