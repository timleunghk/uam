import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'formatDate'
})

export class FormatDatePipe implements PipeTransform {

  transform(dateString: any): Date {
    if(dateString){
      let dateArr = dateString.split('/');
      return new Date( parseInt(dateArr[2]), parseInt(dateArr[1])-1 , parseInt(dateArr[0]) );
    }else{
      return null;
    }
  }
}
