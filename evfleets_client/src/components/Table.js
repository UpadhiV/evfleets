import React, { useState } from 'react';
import { withStyles, makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';

import Paper from '@material-ui/core/Paper';

const StyledTableCell = withStyles((theme) => ({
  head: {
    textAlign: 'center'
  },
  body: {
    fontSize: 14,
    textAlign: 'center'
  },
}))(TableCell);

const StyledTableRow = withStyles((theme) => ({
  root: {
    '&:nth-of-type(odd)': {
      backgroundColor: theme.palette.action.hover,
    },
  },
}))(TableRow);

const useStyles = makeStyles({
  table: {
    minWidth: 700,
  },
  visuallyHidden: {
    border: 0,
    clip: 'rect(0 0 0 0)',
    height: 1,
    margin: -1,
    overflow: 'hidden',
    padding: 0,
    position: 'absolute',
    top: 20,
    width: 1,
  }
});

const headers = [
  {label: 'Route ID', value: 'route_id'}, 
  {label: 'No of buses per route', value: 'No of buses per route'}, 
  {label: 'TCO per route - D ($)', value: 'TCO per route - D'}, 
  {label: 'Level of Service -D', value: 'Level of Service -D'}, 
  {label: 'Emissions -D', value: 'Emissions -D'}, 
  {label: 'Health impact -D', value: 'Health impact -D'}, 
  {label: '', value: ''}, 
  {label: 'TCO per route - E ($)', value: 'TCO per route - E'}, 
  {label: 'Level of Service -E', value: 'Level of Service -E'}, 
  {label: 'Emissions -E', value: 'Emissions -E'}, 
  {label: 'Health impact -E', value: 'Health impact -E'}
]

export default function TableData(props) {
  const classes = useStyles();
  const [orderBy, setOrderBy] = useState(0)
  const [order, setOrder] = useState("asc")
  const { tabledata } = props

  tabledata.sort((a, b) => {
    let orderConst = order === "asc" ? 1 : -1;

    if (a[headers[orderBy].value] < b[headers[orderBy].value]) {
      return orderConst;
    } else if (a[headers[orderBy].value] > b[headers[orderBy].value]) {
      return -orderConst;
    }
    return 0;
  })

  const orderTable = (i) => {
    console.log(i)
    if (orderBy === i) {
      setOrder(order === "asc" ? "desc" : "asc")
    } else {
      setOrder("asc")
      setOrderBy(i)
    }
  }

  const getCellBGColor = (row, header) => {
    if (header === "TCO per route - E") {
      if (row["TCO per route - E"] <= row["TCO per route - D"] * (parseFloat(props.tcoComparison) / 100.0)) {
        return "green"
      }
      return "red"
    } else {
      return "initial"
    }
  }

  const formatMoney = (amount, decimalCount = 2, decimal = ".", thousands = ",") => {
    try {
      decimalCount = Math.abs(decimalCount);
      decimalCount = isNaN(decimalCount) ? 2 : decimalCount;

      const negativeSign = amount < 0 ? "-" : "";

      let i = parseInt(amount = Math.abs(Number(amount) || 0).toFixed(decimalCount)).toString();
      let j = (i.length > 3) ? i.length % 3 : 0;

      return negativeSign + (j ? i.substr(0, j) + thousands : '') + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + thousands) + (decimalCount ? decimal + Math.abs(amount - i).toFixed(decimalCount).slice(2) : "");
    } catch (e) {
      console.log(e)
    }
  }



  return (
    <TableContainer component={Paper} style={{ marginTop: 80 }}>
      <Table className={classes.table} aria-label="customized table">
        <TableHead>
          <TableRow>
            {headers.map((header, i) => (
              <StyledTableCell align={i > 1 ? "right" : "left"} sortDirection={orderBy === i ? order : false}>
                <TableSortLabel
                  active={orderBy === i}
                  direction={orderBy === i ? order : 'asc'}
                  onClick={() => orderTable(i)}
                >
                  {header.label}
                  {orderBy === i ? (
                    <span className={classes.visuallyHidden}>
                      {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                    </span>
                  ) : null}
                </TableSortLabel>
              </StyledTableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {tabledata.map((row) => (
            <StyledTableRow key={row.route_id}>
              <StyledTableCell component="th" scope="row">
                {row.route_id}
              </StyledTableCell>
              <StyledTableCell>{row['No of buses per route']}</StyledTableCell>

              {headers.slice(2).map(header => (
                <StyledTableCell align="right" style={{ backgroundColor: getCellBGColor(row, header.value) }}>
                  {header.label.includes("TCO") ? formatMoney(row[header.value]) : row[header.value]}
                </StyledTableCell>
              ))}
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}