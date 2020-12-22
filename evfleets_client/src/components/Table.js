import React, { useState } from 'react';
import { withStyles, makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import OutlinedInput from '@material-ui/core/OutlinedInput';
import InputAdornment from '@material-ui/core/InputAdornment';



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
  {label: 'No of buses', value: 'No of buses'}, 

  {label: 'TCO per route - D ($/lifetime)', value: 'TCO per route - D'}, 
  {label: 'Level of Service -D', value: 'Level of Service -D'}, 
  {label: 'Emissions -D (ton CO2/yr)', value: 'Emissions -D'}, 
  {label: 'Health impact -D (USD Millions 2020)', value: 'Health impact -D'}, 
  {label: '', value: ''},
  {label: 'TCO <=', value: ''}, 
  {label: 'Emissions <=', value: ''},
  {label: 'Technically Feasible?', value: 'feasible'}, 
  {label: '', value: ''}, 
  {label: 'TCO per route - E ($/lifetime)', value: 'TCO per route - E'}, 
  {label: 'Level of Service -E', value: 'Level of Service -E'}, 
  {label: 'Emissions -E (ton CO2/yr)', value: 'Emissions -E'}, 
  {label: 'Health impact -E (USD Millions 2020)', value: 'Health impact -E'}
]

export default function TableData(props) {
  const classes = useStyles();
  const [orderBy, setOrderBy] = useState(0)
  const [tcoComparison, setTCO] = useState(100)
  const [emissionsComparison, setEmissions] = useState(100)
  const [order, setOrder] = useState("asc")
  const { tabledata } = props

  tabledata.forEach(row => {
    row["tcoComp"] = row["TCO per route - E"] <= row["TCO per route - D"] * (tcoComparison / 100.0) ? true : false;
    row["emissionsComp"] = row["Emissions -E"] <= row["Emissions -D"] * (emissionsComparison / 100.0) ? true : false;
    row["feasible"] = row["tcoComp"] && row["emissionsComp"] ? "yes" : "no";
  })

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
    if (orderBy === i) {
      setOrder(order === "asc" ? "desc" : "asc")
    } else {
      setOrder("asc")
      setOrderBy(i)
    }
  }

  const getCellBGColor = (row, header) => {
    if (header === "TCO per route - E") {
      return row["tcoComp"] ? "green" : "red"
    } else if (header === "Emissions -E") {
      return row["emissionsComp"] ? "green" : "red"
    } else if (header === "feasible") {
      return row["feasible"] === "yes" ? "green" : "red"
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

  const headerCell = (header, i) => (
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
  )



  return (
    <TableContainer component={Paper} style={{ marginTop: 80 }}>
      <Table className={classes.table} aria-label="customized table">
        <TableHead>
          <TableRow>
            {headers.slice(0, 7).map(headerCell)}
            <StyledTableCell>
              {"TCO <="}
              <OutlinedInput 
                id="numeric-tco-comp" 
                endAdornment={<InputAdornment position="end">%</InputAdornment>} 
                inputProps={{min: 0, style: { textAlign: 'center' }}} 
                margin="dense" 
                value={tcoComparison} 
                type="number" 
                onChange={(val) => setTCO(val.target.value)} 
              />
            </StyledTableCell>
            <StyledTableCell>
              {"Emissions <="}
              <OutlinedInput 
                id="numeric-emissions-comp" 
                endAdornment={<InputAdornment position="end">%</InputAdornment>} 
                inputProps={{min: 0, style: { textAlign: 'center' }}} 
                margin="dense" 
                value={emissionsComparison} 
                type="number"
                onChange={(val) => setEmissions(val.target.value)} 
              />
            </StyledTableCell>
            {headers.slice(9).map((header, i) => headerCell(header, i + 9))}
          </TableRow>
        </TableHead>
        <TableBody>
          {tabledata.map((row) => (
            <StyledTableRow key={row.route_id}>
              {headers.map((header, i) => (
                <StyledTableCell align={i > 1 ? "right" : "left"} style={{ backgroundColor: getCellBGColor(row, header.value) }}>
                  {header.label.includes("$") ? formatMoney(row[header.value]) : row[header.value]}
                </StyledTableCell>
              ))}
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}