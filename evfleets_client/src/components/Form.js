import React, { Component } from 'react';
import { withStyles } from "@material-ui/core/styles";

import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Typography from '@material-ui/core/Typography';
import Checkbox from '@material-ui/core/Checkbox';
import ListItemText from '@material-ui/core/ListItemText';
import InputAdornment from '@material-ui/core/InputAdornment';
import FormHelperText from '@material-ui/core/FormHelperText';


import axios from 'axios';
import Paper from '@material-ui/core/Paper';

import Grid from '@material-ui/core/Grid';


const styles = theme => ({
  root: {
    flexGrow: 1,
  },
  formControl: {
    margin: "0 auto",
    minWidth: 220,
    maxWidth: '100%'
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
  paper: {
    padding: theme.spacing(2),
    color: theme.palette.text.secondary,
  }
});

class Form extends Component {

  constructor(props) {
    super(props)

    this.state = {
      'city': '',
      'selectedroutes': [],

      'bus_type': '',
      'bus_cost': 0,
      'utility': 0,
      'fuel_price': 0,
      'demand_charge': 0,
      'dc_efficiency': 0.92,
      'l2_efficiency': 0.0,

      'cities': [],
      'routes': []
    }
  }

  componentDidMount() {
    axios.get('/cities')
      .then((resp) => {
        this.setState(resp.data);
      })
  }

  handleChange = (id) => {
    return (val) => {
      console.log(id, val.target.value)
      if (id === 'city') {
        axios.get("/routes/" + val.target.value)
          .then(resp => {
            this.setState({ routes: resp.data.options, selectedroutes: [] })
          })
      }
      this.setState({ [id]: val.target.value }, () => {
        axios.post("/tabledata", this.state)
          .then(resp => {
            this.props.setTableData(resp.data.data.filter(val => this.state.selectedroutes.includes(val.route_id)))
          })
          .catch(error => {
            console.log(this.state)
          })
      })
    }
  }

  render() {
    const { classes } = this.props;

    return (
      <div className={classes.root}>
        <Grid container spacing={10}>

          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <Typography variant="h4" gutterBottom>
                1. City / Routes
              </Typography>

              <Grid container justify="center">
                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <InputLabel id="city-select-label">Select City</InputLabel>
                    <Select
                      labelId="city-select-label"
                      id="city-select"
                      value={this.state.city}
                      onChange={this.handleChange('city')}
                    >
                      {this.state.cities.map(city => (
                        <MenuItem key={city.value} value={city.value}>{city.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <InputLabel id="routes-select-label">Select routes to analyse</InputLabel>
                    <Select
                      labelId="routes-select-label"
                      id="routes-select"
                      multiple
                      value={this.state.selectedroutes}
                      onChange={this.handleChange('selectedroutes')}
                      input={<Input />}
                      renderValue={(selected) => selected.join(', ')}
                    >
                      {this.state.routes.map((route) => (
                        <MenuItem key={route.value} value={route.value}>
                          <Checkbox checked={this.state.selectedroutes.indexOf(route.value) > -1} />
                          <ListItemText primary={route.label} />
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

              </Grid>
            </Paper>
          </Grid>


          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <Typography variant="h4" gutterBottom>
                2. Price Parameters
              </Typography>

              <Grid container justify="center">
               
                <Grid item xs={3} align="center">
                  <FormControl className={classes.formControl}>
                    <FormHelperText id="fuel-price-helper-text">Fuel price</FormHelperText>
                    <Input 
                      id="numeric-fuel-cost" 
                      endAdornment={<InputAdornment position="end">$/gallon eq</InputAdornment>} 
                      inputProps={{min: 0, style: { textAlign: 'end' }}} 
                      value={this.state.fuel_price} 
                      type="number"
                      onChange={this.handleChange('fuel_price')} 
                    />
                  </FormControl>
                </Grid>

                <Grid item xs={3} align="center">
                  <FormControl className={classes.formControl}>
                    <FormHelperText id="utility-price-helper-text">Cost of Electric Bus</FormHelperText>
                    <Input 
                      id="numeric-bus-cost" 
                      startAdornment={ <InputAdornment position="start">$</InputAdornment> } 
                      value={this.state.bus_cost} 
                      type="number"
                      onChange={this.handleChange('bus_cost')}
                    />
                  </FormControl>
                </Grid>

                <Grid item xs={3} align="center">
                  <FormControl className={classes.formControl}>
                    <FormHelperText id="utility-price-helper-text">Utility charges</FormHelperText>
                    <Input 
                      id="numeric-utility-cost" 
                      endAdornment={<InputAdornment position="end">$/kWh</InputAdornment>} 
                      inputProps={{min: 0, style: { textAlign: 'end' }}} 
                      value={this.state.utility} 
                      type="number"
                      onChange={this.handleChange('utility')} 
                    />
                  </FormControl>
                </Grid>

                <Grid item xs={3} align="center">
                  <FormControl className={classes.formControl}>
                    <FormHelperText id="demand-price-helper-text">Demand Charge</FormHelperText>
                    <Input 
                      id="numeric-demand-cost" 
                      endAdornment={<InputAdornment position="end">$/kW-month</InputAdornment>}
                      inputProps={{min: 0, style: { textAlign: 'end' }}}   
                      value={this.state.demand_charge} 
                      type="number"
                      onChange={this.handleChange('demand_charge')} 
                    />
                  </FormControl>
                </Grid>

              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <Typography variant="h4" gutterBottom>
                3. Vehicle Parameters
              </Typography>

              <Grid container justify="center">

                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <InputLabel id="routes-select-label">Select bus type</InputLabel>
                    <Select
                      labelId="routes-select-label"
                      id="routes-select"
                      value={this.state.bus_type}
                      onChange={this.handleChange('bus_type')}
                      input={<Input />}
                    >
                      {[{ 'label': '30 Feet', 'value': '30ft' }, { 'label': '40 Feet', 'value': '40ft' }, { 'label': '60 Feet', 'value': '60ft' }].map((bus) => (
                        <MenuItem key={bus.value} value={bus.value}>
                          {bus.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={6} align="center">
                  <FormControl className={classes.formControl}>
                    <FormHelperText id="demand-price-helper-text">DC Charging efficiency</FormHelperText>
                    <Input 
                      id="numeric-dc-efficiency" 
                      endAdornment={<InputAdornment position="end">Decimal %</InputAdornment>}
                      inputProps={{min: 0, style: { textAlign: 'end' }}}
                      value={this.state.dc_efficiency} 
                      type="number"
                      onChange={this.handleChange('dc_efficiency')} 
                    />
                  </FormControl>
                </Grid>

              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </div>
    );
  }
}

export default withStyles(styles, { withTheme: true })(Form);
